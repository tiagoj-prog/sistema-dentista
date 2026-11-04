// =========================================================
// MANTÉM A POSIÇÃO DA PÁGINA APÓS ENVIAR FORMULÁRIOS
// =========================================================

(function () {

    const chave =
        "scrollPos:" + window.location.pathname;

    if ("scrollRestoration" in history) {
        history.scrollRestoration = "manual";
    }


    document.addEventListener(
        "submit",
        function () {

            sessionStorage.setItem(
                chave,
                String(window.scrollY)
            );

        }
    );


    window.addEventListener(
        "DOMContentLoaded",
        function () {

            const posicao =
                sessionStorage.getItem(chave);

            if (posicao === null) {
                return;
            }

            setTimeout(
                function () {

                    window.scrollTo({
                        top: Number(posicao),
                        left: 0,
                        behavior: "instant"
                    });

                    sessionStorage.removeItem(
                        chave
                    );

                },
                100
            );

        }
    );

})();