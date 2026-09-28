"""APT is authoritative. No downloaded code, ISO updater or private package format."""
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

STATE = Path('/var/lib/katu-update')
HELPER = '/usr/lib/katu-update/helper'
UNIT = 'katu-update-transaction.service'
SAFE_NAME = re.compile(r'^[a-z0-9][a-z0-9+.-]*(?::[a-z0-9]+)?$')
CRITICAL = ('linux-image', 'linux-headers', 'firmware-', 'grub', 'shim',
            'initramfs', 'systemd', 'libc6', 'libapt', 'dpkg', 'apt')


class UpdateError(RuntimeError):
    pass


def run(args, timeout=120):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                            env={**os.environ, 'LC_ALL': 'C'})
    if result.returncode:
        # Do not persist command output: remote URLs may contain credentials.
        raise UpdateError('Falha em %s (código %s).' % (Path(args[0]).name, result.returncode))
    return result.stdout


def channel():
    path = Path('/etc/apt/sources.list.d/katu.sources')
    if not path.exists():
        return 'não configurado'
    suites = re.findall(r'^Suites:\s*(.+)$', path.read_text(), re.M)
    return suites[0] if len(suites) == 1 and suites[0] in ('stable', 'beta') else 'configuração inválida'


def make_plan(selected=None):
    import apt
    import apt_pkg
    apt_pkg.init_config()
    apt_pkg.config.set('APT::Install-Recommends', 'false')
    cache = apt.Cache()
    if cache.broken_count:
        raise UpdateError('Dependências quebradas. Repare o APT antes de atualizar.')
    if selected is None:
        selected = [p.name for p in cache if p.is_installed and p.is_upgradable
                    and p._pkg.selected_state != apt_pkg.SELSTATE_HOLD]
    for name in selected:
        if not SAFE_NAME.fullmatch(name) or name not in cache:
            raise UpdateError('Pacote inválido ou indisponível.')
        pkg = cache[name]
        if pkg._pkg.selected_state == apt_pkg.SELSTATE_HOLD:
            raise UpdateError('Pacote retido pelo administrador: ' + name)
        pkg.mark_install(auto_fix=True, auto_inst=True, from_user=False)
    if cache.broken_count:
        raise UpdateError('Não foi possível resolver as dependências deste plano.')
    changes = []
    for pkg in cache.get_changes():
        if pkg.marked_delete:
            raise UpdateError('A operação removeria pacotes. Requer revisão administrativa.')
        candidate = pkg.candidate
        if not candidate or not any(origin.trusted for origin in candidate.origins):
            raise UpdateError('Origem não autenticada: ' + pkg.name)
        if pkg.installed and apt_pkg.version_compare(candidate.version, pkg.installed.version) < 0:
            raise UpdateError('Downgrade não autorizado: ' + pkg.name)
        if pkg.installed and candidate.version == pkg.installed.version:
            continue
        if pkg._pkg.selected_state == apt_pkg.SELSTATE_HOLD:
            raise UpdateError('Dependência retida: ' + pkg.name)
        katu_origins = [o for o in candidate.origins if o.origin == 'Katu OS']
        if channel() == 'stable' and any(o.archive == 'beta' for o in katu_origins):
            raise UpdateError('Pacote beta não pode entrar no canal stable.')
        record = candidate.record
        changes.append(dict(name=pkg.name, installed=pkg.installed.version if pkg.installed else '',
                            version=candidate.version, size=candidate.size,
                            sha256=candidate.sha256,
                            automatic=pkg.is_auto_installed or (not pkg.is_installed and pkg.name not in selected),
                            installed_size=candidate.installed_size,
                            origin='Katu' if katu_origins else 'Sistema',
                            category=record.get('X-Katu-Category', 'Segurança' if candidate.is_security_update else 'Sistema'),
                            notes=record.get('X-Katu-Notes', candidate.summary),
                            critical=pkg.name.startswith(CRITICAL)))
    changes.sort(key=lambda item: item['name'])
    identity = [{k: p[k] for k in ('name', 'installed', 'version', 'size', 'sha256')} for p in changes]
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return dict(packages=changes, digest=digest, selected=sorted(selected),
                download=sum(p['size'] for p in changes),
                disk=max(0, cache.required_space), critical=any(p['critical'] for p in changes))


def optional_apps():
    """Offer missing official recommendations; never silently restore removed apps."""
    import apt
    cache = apt.Cache()
    if 'katu-desktop' not in cache or not cache['katu-desktop'].candidate:
        return []
    candidate = cache['katu-desktop'].candidate
    if not any(o.trusted and o.origin == 'Katu OS' for o in candidate.origins):
        return []
    result = []
    for group in candidate.record.get('Recommends', '').split(','):
        name = group.strip().split(' ')[0]
        if SAFE_NAME.fullmatch(name) and name in cache and not cache[name].is_installed:
            result.append(name)
    return sorted(result)


def preflight(plan):
    # Conservative allowance for unpacking, metadata and retained archives.
    required = plan['download'] + plan['disk'] + 256 * 1024 * 1024
    for directory in ('/var/cache/apt/archives', '/usr', '/var/lib/dpkg'):
        if shutil.disk_usage(directory).free < required:
            raise UpdateError('Espaço insuficiente. Libere espaço antes de atualizar.')
    if plan['critical']:
        for battery in Path('/sys/class/power_supply').glob('*'):
            if (battery / 'type').exists() and (battery / 'type').read_text().strip() == 'Battery':
                try:
                    if (battery / 'status').read_text().strip() == 'Discharging' and int((battery / 'capacity').read_text()) < 30:
                        raise UpdateError('Conecte o computador à energia antes da atualização crítica.')
                except (FileNotFoundError, ValueError):
                    raise UpdateError('Não foi possível verificar a bateria.')


def flatpak_plan():
    if not shutil.which('flatpak'):
        return []
    items = []
    for scope in ('user', 'system'):
        output = run(['flatpak', 'remote-ls', '--' + scope, '--updates', '--columns=ref,version'])
        for line in output.splitlines():
            fields = line.split('\t')
            if fields and fields[0].startswith(('app/', 'runtime/')):
                items.append(dict(ref=fields[0], version=fields[1] if len(fields) > 1 else '', scope=scope))
    return items


def read_state():
    try:
        return json.loads((STATE / 'status.json').read_text())
    except (OSError, ValueError):
        return {}


def history():
    try:
        return [json.loads(line) for line in (STATE / 'history.jsonl').read_text().splitlines()][-100:]
    except (OSError, ValueError):
        return []


def verify_versions(plan):
    for package in plan['packages']:
        actual = run(['dpkg-query', '-W', '-f=${db:Status-Status}\t${Version}', package['name']]).strip()
        if actual != 'installed\t' + package['version']:
            raise UpdateError('Validação pós-instalação falhou: ' + package['name'])
    if run(['dpkg', '--audit']).strip():
        raise UpdateError('O dpkg deixou pacotes pendentes. Requer reparação.')
