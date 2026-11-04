(function () {
    const LIMITE_PADRAO = 5;

    function criarBotao(container, totalOcultos, mostrar, onClick) {
        let area = container.nextElementSibling;

        if (!area || !area.classList.contains("more-items-area")) {
            area = document.createElement("div");
            area.className = "more-items-area";
            container.insertAdjacentElement("afterend", area);
        }

        area.innerHTML = "";

        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "more-items-button";

        if (mostrar) {
            botao.textContent = `Mais (${totalOcultos})`;
        } else {
            botao.textContent = "Mostrar menos";
        }

        botao.addEventListener("click", onClick);
        area.appendChild(botao);
    }

    function aplicarEmTabela(tabela) {
        if (tabela.dataset.moreReady === "1") {
            return;
        }

        const corpo = tabela.tBodies && tabela.tBodies[0];

        if (!corpo) {
            return;
        }

        const linhas = Array.from(corpo.rows);
        const limite = parseInt(
            tabela.dataset.moreLimit || LIMITE_PADRAO,
            10
        );

        if (linhas.length <= limite) {
            tabela.dataset.moreReady = "1";
            return;
        }

        tabela.dataset.moreReady = "1";

        let expandido = false;

        function atualizar() {
            linhas.forEach(function (linha, indice) {
                if (expandido || indice < limite) {
                    linha.classList.remove("more-item-hidden");
                } else {
                    linha.classList.add("more-item-hidden");
                }
            });

            criarBotao(
                tabela.closest(".table-container") || tabela,
                linhas.length - limite,
                !expandido,
                function () {
                    expandido = !expandido;
                    atualizar();
                }
            );
        }

        atualizar();
    }

    function aplicarEmLista(container) {
        if (container.dataset.moreReady === "1") {
            return;
        }

        const seletor = container.dataset.moreItem || ":scope > *";
        let itens;

        try {
            itens = Array.from(
                container.querySelectorAll(seletor)
            );
        } catch (erro) {
            itens = Array.from(container.children);
        }

        const limite = parseInt(
            container.dataset.moreLimit || LIMITE_PADRAO,
            10
        );

        if (itens.length <= limite) {
            container.dataset.moreReady = "1";
            return;
        }

        container.dataset.moreReady = "1";

        let expandido = false;

        function atualizar() {
            itens.forEach(function (item, indice) {
                if (expandido || indice < limite) {
                    item.classList.remove("more-item-hidden");
                } else {
                    item.classList.add("more-item-hidden");
                }
            });

            criarBotao(
                container,
                itens.length - limite,
                !expandido,
                function () {
                    expandido = !expandido;
                    atualizar();
                }
            );
        }

        atualizar();
    }

    function aplicarMostrarMais() {
        document.querySelectorAll(
            "table:not([data-no-more])"
        ).forEach(aplicarEmTabela);

        document.querySelectorAll(
            "[data-more-list]"
        ).forEach(aplicarEmLista);
    }

    document.addEventListener(
        "DOMContentLoaded",
        aplicarMostrarMais
    );

    window.aplicarMostrarMais = aplicarMostrarMais;
})();
