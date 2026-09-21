# Katu OS APT Repository

Repositório APT oficial para pacotes customizados do Katu OS.

## Estrutura

```
repository/
├── dists/
│   └── katu/
│       ├── Release
│       └── main/
│           └── binary-amd64/
│               ├── Packages
│               └── Packages.gz
├── pool/
│   └── main/
│       ├── katu-release_1.0_all.deb
│       ├── katu-branding_1.0_all.deb
│       ├── katu-default-settings_1.0_all.deb
│       └── katu-welcome_1.0_all.deb
└── setup-repo.sh
```

## Gerar o Repositório (Linux)

```bash
bash repository/setup-repo.sh
```

O script:
1. Compila os 4 pacotes `.deb` de `packages/`
2. Copia para `repository/pool/main/`
3. Gera `Packages` e `Release` com dpkg-scanpackages
4. Gera índice comprimido `.gz`

## Usar o Repositório Localmente

```bash
echo "deb [trusted=yes] file:///caminho/para/katuos/repository katu main" \
  | sudo tee /etc/apt/sources.list.d/katu-local.list

sudo apt update
sudo apt install katu-welcome
```

## Repositório Futuro

O repositório público será hospedado em `repo.katuos.com.br`.

Linha sources.list futura:
```
deb [signed-by=/etc/apt/keyrings/katuos.gpg] https://repo.katuos.com.br katu main
```
