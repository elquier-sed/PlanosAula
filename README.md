# Sistema de Planos de Aula

Sistema web desenvolvido em Django para criação e gerenciamento de
planejamentos mensais de aula para o **Ensino Fundamental - Anos
Finais** e o **Ensino Médio**.

O sistema permite que professores selecionem dados curriculares
previamente cadastrados, preencham informações pedagógicas do
planejamento e, futuramente, gerem o documento final em PDF.

> **Estado do projeto:** em desenvolvimento. O núcleo de criação do
> planejamento mensal está funcional. Ainda há funcionalidades
> previstas, especialmente o bloco IFA do Ensino Médio,
> edição/visualização completa e geração de PDF.

------------------------------------------------------------------------

## Tecnologias

-   Python 3.13
-   Django 6.1
-   PostgreSQL
-   HTML/CSS
-   JavaScript nativo (`fetch`) para carregamentos dinâmicos

O desenvolvimento atual é realizado em Windows.

------------------------------------------------------------------------

## Estrutura principal

``` text
PlanosAula/
├── cadastros/
├── planejamentos/
├── config/
├── templates/
├── manage.py
└── .venv/          # ambiente local; não deve ser versionado
```

### `cadastros`

Contém os cadastros administrativos e curriculares utilizados pelo
sistema, entre eles:

-   Etapas de Ensino
-   Séries/Anos
-   Áreas do Conhecimento
-   Disciplinas
-   vínculo Série/Disciplina
-   Competências
-   Habilidades
-   Habilidades do Currículo Digital
-   Competências comuns IFA
-   Objetivos de Aprendizagem IFA
-   Critérios de Avaliação
-   Instrumentos de Avaliação
-   Recursos Pedagógicos
-   Referências
-   Escolas
-   Professores

### `planejamentos`

Contém o fluxo do planejamento mensal:

-   modelo `PlanejamentoMensal`;
-   `ModelForm`;
-   views;
-   endpoints AJAX;
-   templates do professor;
-   regras de filtragem dinâmica EF/EM.

### `config`

Configuração principal do projeto Django e roteamento geral.

------------------------------------------------------------------------

## Ambiente de desenvolvimento atual

O projeto está atualmente sendo executado em:

``` text
C:\Projetos\PlanosAula
```

Ambiente virtual:

``` text
.venv
```

Banco PostgreSQL utilizado no desenvolvimento:

``` text
planos_aula
```

Servidor PostgreSQL:

``` text
localhost:5432
```

As credenciais do banco **não devem ser documentadas neste README nem
enviadas ao Git**.

------------------------------------------------------------------------

## Preparação do ambiente

> Esta seção será revisada quando o `requirements.txt` e a configuração
> por variáveis de ambiente forem finalizados.

### 1. Clonar ou copiar o projeto

Após o projeto estar disponível em Git:

``` powershell
git clone <URL_DO_REPOSITORIO>
cd PlanosAula
```

Enquanto ainda não estiver versionado, utilize uma cópia da pasta do
projeto.

### 2. Criar ambiente virtual

No Windows/PowerShell:

``` powershell
python -m venv .venv
```

Ativar:

``` powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

Quando o `requirements.txt` estiver disponível:

``` powershell
pip install -r requirements.txt
```

### 4. PostgreSQL

É necessário ter PostgreSQL instalado e criar/configurar o banco
utilizado pelo projeto.

O ambiente atual utiliza:

``` text
Banco: planos_aula
Host: localhost
Porta: 5432
```

A configuração definitiva das credenciais será migrada para variáveis de
ambiente antes da publicação do repositório.

### 5. Migrations

Em uma instalação nova, após configurar o banco:

``` powershell
python manage.py migrate
```

Se for utilizado o backup do banco de desenvolvimento entregue junto ao
projeto, seguir o procedimento específico de restauração antes de
executar alterações no banco.

### 6. Criar superusuário

Caso necessário:

``` powershell
python manage.py createsuperuser
```

### 7. Verificar o projeto

``` powershell
python manage.py check
```

O resultado esperado é:

``` text
System check identified no issues (0 silenced).
```

### 8. Executar o servidor

``` powershell
python manage.py runserver
```

A aplicação de desenvolvimento ficará disponível normalmente em:

``` text
http://127.0.0.1:8000/
```

Admin:

``` text
http://127.0.0.1:8000/admin/
```

------------------------------------------------------------------------

## Fluxo atual

O fluxo principal implementado é:

``` text
Login
  ↓
Meus Planejamentos
  ↓
Novo Planejamento
  ↓
Escola
  ↓
Série/Ano
  ↓
Disciplina
  ↓
Dados curriculares e pedagógicos
  ↓
Salvar
```

Ao selecionar uma série, o sistema carrega dinamicamente apenas as
disciplinas disponíveis para ela.

Ao selecionar uma disciplina, as competências, habilidades e informações
do Currículo Digital são carregadas conforme as regras da etapa de
ensino.

------------------------------------------------------------------------

## Regras curriculares importantes

Estas regras são essenciais para manutenção do sistema.

### Determinação da etapa

A etapa do planejamento deve ser determinada por:

``` python
serie.etapa
```

**Não utilizar `disciplina.area_conhecimento` para decidir se o
planejamento é EF ou EM.**

Uma disciplina como Artes pode possuir Área do Conhecimento e também
estar vinculada a uma série do Ensino Fundamental.

### Ensino Fundamental - Anos Finais

**Competências**

São filtradas por:

``` text
Etapa + Disciplina
```

**Habilidades regulares**

São filtradas por:

``` text
Etapa + Disciplina
```

A `serie_origem` da habilidade é apenas informação de origem.

**Não restringir as habilidades pela série de origem.**

Uma habilidade originária de outra série pode ser utilizada pelo
professor.

**Currículo Digital**

É filtrado pela série selecionada.

### Ensino Médio

Cada disciplina está relacionada a uma Área do Conhecimento.

**Competências**

São obtidas pela área da disciplina.

``` text
Disciplina
   ↓
Área do Conhecimento
   ↓
Competências
```

**Habilidades regulares**

São vinculadas às competências.

Na interface, as habilidades aparecem dinamicamente conforme o professor
marca ou desmarca competências.

``` text
Competência selecionada
        ↓
Habilidades da competência
```

**Currículo Digital**

As habilidades cadastradas para o EM são comuns às séries.

No banco:

``` text
etapa = Ensino Médio
serie = NULL
```

### Recomposição da Aprendizagem

Os campos:

-   Habilidades para Recomposição
-   Caminho Metodológico da Recomposição

aparecem somente para:

-   Língua Portuguesa
-   Matemática

A regra vale para EF e EM.

### Avaliação

**Instrumentos de Avaliação:** disponíveis para EF e EM.

**Critérios de Avaliação - Currículo Digital:** disponíveis somente para
o Ensino Médio.

### Recursos e Referências

Recursos Pedagógicos e Referências são catálogos globais, disponíveis
para EF e EM.

------------------------------------------------------------------------

## Campos atualmente disponíveis no planejamento

### Identificação

-   Escola
-   Mês
-   Ano
-   Série/Ano
-   Disciplina
-   Quantidade de Aulas

### Competências e habilidades

-   Competências
-   Habilidades
-   Outras Habilidades
-   Habilidades do Currículo Digital
-   Outras Habilidades do Currículo Digital
-   Objetos de Conhecimento
-   Caminho Metodológico

### Recomposição

Somente Português e Matemática:

-   Habilidades para Recomposição
-   Caminho Metodológico da Recomposição

### Recursos Pedagógicos

-   Recursos Pedagógicos
-   Outro Recurso Pedagógico

### Avaliação

-   Critérios de Avaliação - Currículo Digital (somente EM)
-   Instrumentos de Avaliação
-   Outro Instrumento de Avaliação

### Referências

-   Referências
-   Outra Referência

------------------------------------------------------------------------

## Rotas relevantes

  -------------------------------------------------------------------------------------
  Rota                          Nome                            Função
  ----------------------------- ------------------------------- -----------------------
  `/`                           `lista_planejamentos`           Lista os planejamentos
                                                                do professor

  `/novo/`                      `novo_planejamento`             Cria planejamento

  `/ajax/disciplinas/`          `carregar_disciplinas`          Carrega disciplinas da
                                                                série

  `/ajax/dados-curriculares/`   `carregar_dados_curriculares`   Carrega competências e
                                                                Currículo Digital

  `/ajax/habilidades/`          `carregar_habilidades`          Carrega habilidades
                                                                regulares

  `/admin/`                     Django Admin                    Administração dos
                                                                cadastros

  `/contas/`                    Auth Django                     Login/logout
  -------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Observação sobre JavaScript e Django

No JavaScript, a função de carregamento das habilidades é:

``` javascript
carregarHabilidades()
```

No Django, a view/URL utiliza:

``` python
carregar_habilidades
```

Não confundir os dois nomes.

------------------------------------------------------------------------

## Dados curriculares

Já foram cadastrados/importados dados referentes a:

-   etapas;
-   séries;
-   disciplinas;
-   vínculos Série/Disciplina;
-   competências EF;
-   competências EM;
-   habilidades EF;
-   habilidades EM;
-   Currículo Digital;
-   competências comuns IFA;
-   critérios de avaliação do Currículo Digital EM;
-   instrumentos de avaliação;
-   recursos pedagógicos;
-   referências;
-   objetivos de aprendizagem IFA.

Os arquivos de importação devem ser preservados junto à documentação do
projeto.

Também deve ser entregue ao novo desenvolvedor um backup do banco
PostgreSQL de desenvolvimento.

------------------------------------------------------------------------

## Funcionalidades pendentes

As próximas etapas previstas incluem:

-   concluir os campos específicos de IFA do Ensino Médio;
-   Nome do Projeto Integrador;
-   Competências Comuns dos Itinerários Formativos;
-   Objetivos Gerais de Aprendizagem IFA;
-   Objetivos Específicos de Aprendizagem IFA;
-   dependência Objetivo Geral → Objetivos Específicos;
-   Caminho Metodológico do Projeto Integrador;
-   Quantidade de Aulas IFA;
-   edição de planejamento;
-   restauração das seleções dinâmicas ao editar ou após erro de
    validação;
-   visualização detalhada;
-   geração de PDF;
-   fluxo de finalização do planejamento;
-   avaliar cópia do planejamento do mês anterior;
-   testes automatizados;
-   preparação para produção/hospedagem.

------------------------------------------------------------------------

## Pontos técnicos a revisar

Antes de grandes refatorações, recomenda-se reproduzir e testar os
fluxos atuais de EF e EM.

Pontos já identificados para revisão:

-   validação amigável da unicidade do planejamento;
-   garantir associação do professor antes das validações que dependem
    dele;
-   preservar seleções dinâmicas na futura edição;
-   avaliar criação de um código estável para `EtapaEnsino`, evitando
    regras dependentes do texto do nome;
-   manter validações de regras de negócio no backend, além das regras
    de exibição em JavaScript;
-   criar testes de regressão para as diferenças EF/EM.

------------------------------------------------------------------------

## Testes manuais mínimos

Antes de considerar uma alteração estável, testar pelo menos:

**EF**

``` text
Série EF → Artes
```

Confirmar competências, habilidades e Currículo Digital.

``` text
Série EF → Matemática
```

Confirmar também Recomposição.

**EM**

``` text
Série EM → Física ou Artes
```

Confirmar competências da área e habilidades dinâmicas conforme
competências selecionadas.

``` text
Série EM → Língua Portuguesa ou Matemática
```

Confirmar também Recomposição.

No EM, confirmar ainda a presença dos Critérios de Avaliação - Currículo
Digital.

------------------------------------------------------------------------

## Segurança e versionamento

Não enviar ao Git:

-   `.venv`;
-   senhas;
-   credenciais PostgreSQL;
-   arquivo `.env` real;
-   caches Python;
-   arquivos temporários;
-   dumps de banco contendo informações que não devam ser públicas;
-   `SECRET_KEY` de produção.

Serão preparados antes do primeiro envio ao Git:

-   `.gitignore`;
-   `.env.example`;
-   `requirements.txt`;
-   documentação complementar.

------------------------------------------------------------------------

## Documentação complementar

Além deste README, existe um **Documento de Transferência Técnica** com
detalhes sobre:

-   arquitetura;
-   modelos;
-   decisões de negócio;
-   estado atual;
-   próximos passos;
-   checklist de transferência.

Recomenda-se que o novo desenvolvedor leia esse documento antes de
realizar alterações estruturais.

------------------------------------------------------------------------

## Situação do repositório

O projeto ainda não foi publicado em Git.

O processo de criação do repositório, primeiro commit e envio ao
repositório remoto será realizado após a revisão dos arquivos que podem
conter credenciais ou configurações locais.

------------------------------------------------------------------------

## Status

**Em desenvolvimento.**

O núcleo de criação do Planejamento Mensal está funcional para EF e EM.
A prioridade seguinte é concluir os campos específicos do Ensino
Médio/IFA e, posteriormente, implementar edição, visualização e geração
de PDF.
