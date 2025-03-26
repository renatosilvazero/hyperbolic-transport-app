# Hyperbolic Transport Network Analyzer

Este aplicativo Streamlit simula redes de transporte urbano baseadas em geometria hiperbólica. Ele gera interseções aleatórias, conecta nós com base na distância hiperbólica, simula rotas de tráfego e transporte público, e encontra os caminhos mais eficientes entre dois pontos para diferentes modos de transporte.

## Funcionalidades

- **Geometria Hiperbólica**: Conexões eficientes de longa distância
- **Roteamento Multi-Modal**: Compare caminhada, direção e transporte público
- **Simulação Dinâmica**: Efeitos de tráfego em horários de pico
- **Redes Persistentes**: Parâmetros preservados entre execuções

## Como Usar

1. **Configure os Parâmetros** na barra lateral.
2. Clique em **Generate New Network** ao alterar os parâmetros.
3. Selecione os nós de início/fim do maior componente conectado.
4. Clique em **Calculate Optimal Routes** para comparar modos de transporte.

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/renatosilvazero/hyperbolic-transport-app.git
    ```
2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o aplicativo:
    ```bash
    streamlit run app.py
    ```

## Exemplo de Uso

![Exemplo de Rede de Transporte](exemplo_rede_transporte.png)

## Licença

Este projeto está licenciado sob a Licença CC0 1.0 Universal. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

## Autor

Renato
