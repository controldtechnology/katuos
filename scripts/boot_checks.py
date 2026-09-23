"""Fail-closed checks for the supported amd64 Debian Live layout."""
import re
import shlex
import struct
import hashlib
import subprocess
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(*args):
    return subprocess.run([str(a) for a in args], check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def rooted(root, name):
    """Resolve rootfs links without following absolute links into the host."""
    parts, resolved, links = list(Path(name.lstrip('/')).parts), [], 0
    while parts:
        part = parts.pop(0)
        if part == '..':
            require(bool(resolved), 'Path escapes rootfs')
            resolved.pop()
            continue
        if part == '.':
            continue
        path = root.joinpath(*resolved, part)
        if path.is_symlink():
            links += 1
            require(links < 40, 'Symlink loop')
            target = path.readlink()
            if target.is_absolute():
                resolved = []
            parts = list(target.parts[1:] if target.is_absolute() else target.parts) + parts
        else:
            resolved.append(part)
    return root.joinpath(*resolved)


def kernel_version(path):
    data = path.read_bytes()
    require(data[0x202:0x206] == b'HdrS', f'Invalid x86 kernel: {path}')
    offset = struct.unpack_from('<H', data, 0x20e)[0] + 0x200
    version = data[offset:].split(b'\0', 1)[0].decode('ascii').split()[0]
    require(re.fullmatch(r'[0-9][\w.+-]+', version), 'Invalid kernel version')
    return version


def grub_entries(path, iso_root=None):
    variables, entries, current = {}, [], None
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith('set '):
            tokens = shlex.split(line[4:])
            if len(tokens) == 1 and '=' in tokens[0]:
                key, value = tokens[0].split('=', 1)
                variables[key] = value
        if line.startswith('menuentry '):
            current = {'name': shlex.split(line)[1], 'initrds': []}
        tokens = shlex.split(line, comments=True)
        if not tokens or tokens[0] not in ('linux', 'linuxefi', 'initrd', 'initrdefi'):
            continue
        require(current is not None, f'{path}: boot command outside menuentry')
        expanded = []
        for token in tokens[1:]:
            token = re.sub(r'\$\{(\w+)\}|\$(\w+)',
                           lambda m: variables.get(m[1] or m[2], m[0]), token)
            expanded.extend(shlex.split(token))
        if tokens[0] in ('linux', 'linuxefi'):
            require(len(expanded) > 1, f'{path}: missing kernel parameters')
            require('boot=live' in expanded, f'{path}: missing boot=live (unattended rewrite?)')
            require(not any(x.startswith('boot=casper') or x.startswith('root=') for x in expanded),
                    f'{path}: mixed Live/root boot model')
            current.update(kernel=expanded[0], params=expanded[1:])
            entries.append(current)
            references = expanded[:1]
        else:
            current['initrds'].extend(expanded)
            references = expanded
        for ref in references:
            require(ref.startswith('/') and not any(c in ref for c in '$*?[]'),
                    f'{path}: unresolved boot path {ref}')
            require('..' not in Path(ref).parts, f'{path}: unsafe path')
            if iso_root:
                require(rooted(iso_root, ref).is_file(), f'{path}: missing {ref}')
    require(entries and all(e['initrds'] for e in entries), f'{path}: missing kernel/initrd pairs')
    return entries


def initrd_check(initrd, version, scratch, kernel_config):
    destination = scratch / 'initrd'
    run('unmkinitramfs', initrd, destination)
    root = next((r for r in [destination / 'main', destination] if (r / 'scripts/live').is_file()), None)
    require(root is not None, 'Initrd missing /scripts/live')
    for script in ['9990-main.sh', '9990-misc-helpers.sh', '9990-overlay.sh']:
        require(rooted(root, '/lib/live/boot/' + script).is_file(), f'Initrd missing {script}')
    modules = rooted(root, '/lib/modules')
    require(modules.is_dir(), 'Initrd has no modules')
    versions = {p.name for p in modules.iterdir() if p.is_dir()}
    require(versions == {version}, f'Kernel/initrd mismatch: {version} vs {versions}')
    # initramfs-tools can place modules in an earlier, uncompressed CPIO member.
    names = {p.name.split('.ko')[0].replace('-', '_') for p in destination.rglob('*.ko*')}
    all_versions = {p.name for p in destination.rglob('modules') if p.is_dir()
                    for p in p.iterdir() if p.is_dir()}
    require(all_versions == {version}, f'Initrd CPIO members have mismatched modules: {all_versions}')
    configs = dict(re.findall(r'^(CONFIG_\w+)=(\w+)$', kernel_config, re.M))
    for module, option in {
        'ahci': 'SATA_AHCI', 'ata_piix': 'ATA_PIIX', 'sd_mod': 'BLK_DEV_SD',
        'sr_mod': 'BLK_DEV_SR', 'nvme': 'BLK_DEV_NVME', 'usb_storage': 'USB_STORAGE',
        'uas': 'USB_UAS', 'xhci_pci': 'USB_XHCI_PCI', 'ehci_pci': 'USB_EHCI_PCI',
        'isofs': 'ISO9660_FS', 'loop': 'BLK_DEV_LOOP',
        'squashfs': 'SQUASHFS', 'overlay': 'OVERLAY_FS',
    }.items():
        require(module in names or configs.get('CONFIG_' + option) == 'y',
                f'Initrd missing driver {module} and kernel does not build it in')
    return root


def rootfs_check(root, version):
    for name in ['etc', 'usr', 'var', 'bin', 'sbin', 'lib', 'lib64']:
        require(rooted(root, name).is_dir(), f'Rootfs missing {name}')
    init = rooted(root, '/sbin/init')
    require(init.is_file() and init.name == 'systemd' and init.stat().st_mode & 0o111,
            'Rootfs init is not executable systemd')
    modules = rooted(root, '/lib/modules')
    require({p.name for p in modules.iterdir() if p.is_dir()} == {version},
            'Rootfs modules do not match kernel')
    return rooted(root, '/boot/config-' + version).read_text()
