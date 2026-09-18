# 7-Zip GUI para macOS (Intel) — build automático via GitHub Actions

App de código aberto em Python/Tkinter para compactar e extrair arquivos
`.7z`, `.zip`, `.tar`, `.tar.gz` e `.tar.bz2`. Não depende de nenhum
binário externo (Homebrew, p7zip etc.) — usa a biblioteca Python pura
**py7zr** para o formato `.7z`, então o `.app` gerado funciona sozinho.

## Estrutura dos arquivos

```
sevenzip-gui/
├── sevenzip_gui.py                 # código-fonte do app (Tkinter)
├── setup.py                        # configuração do py2app (gera o .app)
├── requirements.txt                # dependências Python
├── .gitignore
└── .github/
    └── workflows/
        └── build-dmg.yml           # workflow que compila e gera o .dmg
```

## Passo a passo no GitHub

1. **Crie um repositório novo** no GitHub (público ou privado).
2. **Suba estes arquivos** mantendo a mesma estrutura de pastas acima
   (o `.github/workflows/build-dmg.yml` precisa ficar exatamente nesse
   caminho):

   ```bash
   cd sevenzip-gui
   git init
   git add .
   git commit -m "Primeira versão do 7-Zip GUI"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
   git push -u origin main
   ```

3. Assim que o push chegar na branch `main`, a aba **Actions** do
   repositório vai mostrar o workflow **"Build macOS .dmg (Intel)"**
   rodando automaticamente.
4. Quando terminar (uns 3–5 minutos), abra a execução do workflow e
   baixe o artefato **`7ZipGUI-dmg`** — dentro dele está o
   `7ZipGUI.dmg` pronto.

### Gerar uma Release oficial com o .dmg anexado

Se quiser uma página de "Releases" no GitHub com o `.dmg` para download
direto, crie uma tag no formato `v1.0.0`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

O workflow detecta tags que começam com `v` e publica o `.dmg`
automaticamente em **Releases** (usa a action `softprops/action-gh-release`,
sem precisar configurar nada extra — o `GITHUB_TOKEN` já é fornecido pelo
próprio GitHub Actions).

## Sobre a compatibilidade com macOS antigos (Intel)

- O workflow roda no runner **`macos-15-intel`**, que no momento é o
  **último runner com arquitetura x86_64 (Intel)** oferecido pelo GitHub
  (os runners `macos-latest`/`macos-14`+ já são Apple Silicon/arm64 e
  gerariam um binário incompatível com Macs Intel). A Apple e o GitHub
  já sinalizaram a descontinuação gradual do Intel nos runners hospedados
  — se esse label parar de existir no futuro, você vai precisar hospedar
  seu próprio runner Intel (self-hosted) para continuar compilando para
  essa arquitetura.
- A variável `MACOSX_DEPLOYMENT_TARGET` no workflow (`10.13`, High Sierra
  — 2017) define a versão mínima de macOS que o app aceita rodar. Você
  pode tentar baixar para `10.9`, mas o resultado depende de qual versão
  do Python for usada para compilar: instaladores oficiais recentes do
  Python 3.11/3.12 já exigem macOS relativamente moderno mesmo em Intel.
  Se precisar do alcance máximo possível, teste também com
  `python-version: "3.9"` no workflow, que tende a aceitar sistemas mais
  antigos.
- O app é assinado apenas de forma **ad-hoc** (gratuita, sem conta Apple
  Developer). Isso evita o erro "app está danificado", mas o Gatekeeper
  ainda vai avisar "desenvolvedor não identificado" no primeiro clique.
  O usuário pode abrir mesmo assim: clique direito no app → **Abrir** →
  confirmar. Assinatura completa + notarização exigem conta paga da Apple
  Developer Program (US$ 99/ano) e não estão neste workflow gratuito.

## Testar/compilar localmente antes de subir pro GitHub (opcional)

Se você já tiver um Mac Intel à mão:

```bash
pip3 install -r requirements.txt
python3 setup.py py2app
# gera dist/7ZipGUI.app
```

## Créditos / licenças

- Motor de compressão `.7z`: [py7zr](https://github.com/miurahr/py7zr)
  (licença LGPL 2.1+), que por sua vez reimplementa o formato aberto
  7-Zip (originalmente por Igor Pavlov, licença LGPL).
- Empacotamento: [py2app](https://py2app.readthedocs.io/) (licença MIT).
