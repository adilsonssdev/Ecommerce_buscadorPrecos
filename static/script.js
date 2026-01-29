document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchTermInput = document.getElementById('search-term');
    const resultsGrid = document.getElementById('results-grid');
    const resultsInfo = document.getElementById('results-info');
    const loader = document.getElementById('loader');

    const sortSelect = document.getElementById('sort-select');
    const resultsHeader = document.querySelector('.results-header');
    const homeView = document.getElementById('home-view');
    const searchView = document.getElementById('search-view');
    const storeFiltersContainer = document.getElementById('store-filters');
    const brandFiltersContainer = document.getElementById('brand-filters');
    const cepTrigger = document.getElementById('cep-trigger');
    const cepDisplay = document.getElementById('cep-display');

    // Modal CEP Elements
    const modalCep = document.getElementById('modal-cep');
    const modalCepInput = document.getElementById('modal-cep-input');
    const btnConfirmarCep = document.getElementById('btn-confirmar-cep');
    const closeModal = document.querySelector('.close-modal');
    const cepStatus = document.getElementById('cep-status');
    const addressPreview = document.getElementById('address-preview');
    const addressText = document.getElementById('address-text');

    let currentProducts = [];
    let userZipCode = "";

    const megamenu = document.getElementById('megamenu');
    const btnCategories = document.getElementById('btn-categories');

    // Função para resetar todos os filtros da sidebar
    function resetFilters() {
        const filters = document.querySelectorAll('.results-sidebar input[type="checkbox"], .results-sidebar input[type="radio"]');
        filters.forEach(filter => {
            if (filter.name === 'price') {
                filter.checked = false;
            } else {
                filter.checked = true; // Lojas marcadas por padrão
            }
        });
        // Sincronizar qualquer seletor de ordenação se necessário
        sortSelect.value = 'relevance';
    }

    // Função centralizada de busca
    async function performSearch(searchTerm) {
        if (!searchTerm) return;

        searchTermInput.value = searchTerm;

        // Resetar Filtros ao iniciar nova busca
        resetFilters();

        // Trocar para visualização de busca
        homeView.style.display = 'none';
        searchView.style.display = 'block';
        loader.style.display = 'block';
        resultsHeader.style.display = 'none';
        resultsGrid.innerHTML = '';
        resultsInfo.innerHTML = '';
        brandFiltersContainer.innerHTML = ''; // Limpar marcas
        const priceFiltersContainer = document.getElementById('price-filters');
        if (priceFiltersContainer) priceFiltersContainer.innerHTML = ''; // Limpar preços

        try {
            const isGitHubPages = window.location.hostname.includes('github.io');
            const apiUrl = isGitHubPages ? `https://raw.githubusercontent.com/${window.location.pathname.split('/')[1]}/${window.location.pathname.split('/')[1]}/main/static/fallback_data.json` : `/api/buscar/${encodeURIComponent(searchTerm)}`;

            const response = await fetch(isGitHubPages ? apiUrl : `/api/buscar/${encodeURIComponent(searchTerm)}`);

            if (!response.ok) {
                if (isGitHubPages) {
                    throw new Error("Modo Estático: A busca em tempo real requer o servidor Python rodando localmente.");
                }
                throw new Error("Erro na busca");
            }

            const data = await response.json();
            loader.style.display = 'none';

            if (data.sucesso && data.produtos.length > 0) {
                // Filtragem de Relevância: Garantir que o termo de busca (ou palavras chave) esteja no nome
                const queryWords = searchTerm.toLowerCase().split(' ').filter(w => w.length > 2);

                // Mapeamento de sinônimos comuns para melhorar a precisão
                const synonyms = {
                    'geladeira': ['refrigerador', 'refrigeradores'],
                    'refrigerador': ['geladeira'],
                    'tv': ['televisor', 'televisão', 'smart tv'],
                    'televisão': ['tv', 'smart tv'],
                    'maquina de lavar': ['lavadora', 'lava e seca'],
                    'notebook': ['laptop'],
                    'smartphone': ['celular', 'iphone', 'smartphones'],
                    'smartphones': ['celular', 'iphone', 'smartphone'],
                    'iphone': ['apple', 'smartphone']
                };

                // Função de normalização simples para PT-BR
                const normalize = (w) => {
                    let word = w.toLowerCase().trim();
                    if (word.endsWith('s') && word.length > 4) return word.slice(0, -1);
                    return word;
                };

                const normalizedQuery = queryWords.map(normalize);

                currentProducts = data.produtos.filter(product => {
                    const productName = product.nome.toLowerCase();
                    // Verifica se alguma palavra da busca (normalizada) está no nome OR algum sinônimo
                    const hasMatch = normalizedQuery.some(word => {
                        if (productName.includes(word)) return true;

                        // Verifica sinônimos da palavra original e da normalizada
                        const originalWord = queryWords[normalizedQuery.indexOf(word)];
                        const totalSynonyms = [
                            ...(synonyms[originalWord] || []),
                            ...(synonyms[word] || [])
                        ];

                        return totalSynonyms.some(s => productName.includes(s.toLowerCase()));
                    });
                    return hasMatch;
                });

                if (currentProducts.length > 0) {
                    resultsHeader.style.display = 'flex';
                    resultsInfo.textContent = `🏆 Encontramos ${currentProducts.length} ofertas relevantes para "${searchTerm}".`;
                    updateStoreFilters(currentProducts);
                    updateBrandFilters(currentProducts);
                    updatePriceFilters(currentProducts); // Nova função
                    renderProducts(currentProducts);
                } else {
                    resultsHeader.style.display = 'none';
                    resultsInfo.textContent = `😕 Nenhum produto suficientemente relevante para "${searchTerm}".`;
                }
            } else {
                resultsHeader.style.display = 'none';
                resultsInfo.textContent = `😕 Nenhum produto encontrado para "${searchTerm}".`;
            }
        } catch (error) {
            loader.style.display = 'none';
            resultsInfo.innerHTML = `<span style="color: red;">Erro ao buscar: ${error.message}</span>`;
        }
    }

    // Listener para links do megamenu (Delegação)
    megamenu.addEventListener('click', (e) => {
        const link = e.target.closest('.cat-link');
        if (link) {
            e.preventDefault();
            const searchTerm = link.getAttribute('data-search');
            megamenu.classList.remove('active');
            performSearch(searchTerm);
        }
    });

    // Listener para categorias da sidebar (Delegação)
    document.addEventListener('click', (e) => {
        const item = e.target.closest('.category-item');
        if (item) {
            const searchTerm = item.getAttribute('data-search');
            performSearch(searchTerm);
        }
    });

    // Toggle do Megamenu
    btnCategories.addEventListener('click', (e) => {
        e.stopPropagation();
        megamenu.classList.toggle('active');
    });

    // Listener para grupos de categorias na sidebar (Accordion)
    document.querySelectorAll('.category-group-header').forEach(header => {
        header.addEventListener('click', () => {
            header.parentElement.classList.toggle('active');
        });
    });

    // Listener para o CEP (Abre Modal)
    cepTrigger.addEventListener('click', () => {
        modalCep.classList.add('active');
        modalCepInput.focus();
    });

    closeModal.addEventListener('click', () => {
        modalCep.classList.remove('active');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modalCep) {
            modalCep.classList.remove('active');
        }
    });

    // Máscara de CEP (xxxxx-xxx)
    modalCepInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 5) {
            value = value.substring(0, 5) + '-' + value.substring(5, 8);
        }
        e.target.value = value;

        // Se completar o CEP, busca o endereço
        if (value.length === 9) {
            lookupCep(value.replace('-', ''));
        } else {
            resetCepStatus();
        }
    });

    async function lookupCep(cep) {
        cepStatus.textContent = "Buscando...";
        cepStatus.className = "cep-status";

        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await response.json();

            if (data.erro) {
                cepStatus.textContent = "CEP não encontrado.";
                cepStatus.className = "cep-status error";
                addressPreview.style.display = 'none';
                document.getElementById('cep-check-icon').classList.remove('active');
                btnConfirmarCep.disabled = true;
            } else {
                cepStatus.textContent = "CEP aplicado";
                cepStatus.className = "cep-status success";
                document.getElementById('cep-check-icon').classList.add('active');

                const fullAddress = `${data.bairro}, ${data.localidade} - ${data.uf}`;
                addressText.textContent = fullAddress;
                addressPreview.style.display = 'flex';
                btnConfirmarCep.disabled = false;

                // Armazena temporariamente
                modalCepInput.dataset.city = data.localidade;
                modalCepInput.dataset.full = fullAddress;
            }
        } catch (error) {
            console.error("Erro ao buscar CEP:", error);
            cepStatus.textContent = "Erro ao validar CEP.";
            cepStatus.className = "cep-status error";
        }
    }

    function resetCepStatus() {
        cepStatus.textContent = "";
        addressPreview.style.display = 'none';
        document.getElementById('cep-check-icon').classList.remove('active');
        btnConfirmarCep.disabled = true;
    }

    btnConfirmarCep.addEventListener('click', () => {
        userZipCode = modalCepInput.value;
        const city = modalCepInput.dataset.city;
        const fullAddress = modalCepInput.dataset.full;

        cepDisplay.textContent = `${city} - ${userZipCode}`;
        modalCep.classList.remove('active');

        // Atualiza a loja mais próxima e faz a busca se estiver na tela de busca
        searchNearestStore(city, fullAddress);

        // Se já houver um termo de busca, refaz a pesquisa para atualizar o contexto regional
        if (searchTermInput.value) {
            searchForm.dispatchEvent(new Event('submit'));
        }
    });

    function searchNearestStore(city, fullAddress = "") {
        // Simulação de busca de loja mais próxima
        const stores = [
            { name: "Magalu", icon: "fa-bag-shopping", prefix: "fa-solid", url: "https://www.magazineluiza.com.br" },
            { name: "Amazon Hub", icon: "fa-amazon", prefix: "fa-brands", url: "https://www.amazon.com.br" },
            { name: "Casas Bahia", icon: "fa-house", prefix: "fa-solid", url: "https://www.casasbahia.com.br" },
            { name: "Fast Shop", icon: "fa-bolt", prefix: "fa-solid", url: "https://www.fastshop.com.br" },
            { name: "Ponto", icon: "fa-location-dot", prefix: "fa-solid", url: "https://www.pontofrio.com.br" }
        ];
        const store = stores[Math.floor(Math.random() * stores.length)];

        let storeAlert = document.getElementById('store-near-alert');
        if (!storeAlert) {
            storeAlert = document.createElement('div');
            storeAlert.id = 'store-near-alert';
            storeAlert.className = 'store-alert-box';

            const resultsContainer = document.querySelector('.main-content');
            if (resultsContainer) {
                resultsContainer.insertBefore(storeAlert, resultsContainer.firstChild);
            }
        }

        storeAlert.innerHTML = `
            <div class="store-alert-icon">
                <i class="${store.prefix} ${store.icon}"></i>
            </div>
            <div class="store-alert-info">
                <h3>Loja mais próxima: <span>${store.name}</span></h3>
                <p>Retire em até 2h em <strong>${city}</strong></p>
                <small>${fullAddress}</small>
            </div>
            <div class="store-alert-action">
                <a href="${store.url}" target="_blank" class="store-alert-button">
                    Ir para loja <i class="fa-solid fa-chevron-right"></i>
                </a>
            </div>
        `;
    }


    // Listener para ordenação
    sortSelect.addEventListener('change', () => {
        const sortedProducts = sortProducts(currentProducts, sortSelect.value);
        renderProducts(sortedProducts);
    });

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        performSearch(searchTermInput.value.trim());
    });

    function applyFilters() {
        const checkedStores = Array.from(storeFiltersContainer.querySelectorAll('input:checked')).map(input => input.value.trim().toLowerCase());
        const checkedBrands = Array.from(brandFiltersContainer.querySelectorAll('input:checked')).map(input => input.value.trim().toUpperCase());
        const checkedPrices = Array.from(document.querySelectorAll('#price-filters input:checked')).map(input => input.value);

        const matchesStore = (p) => checkedStores.length === 0 || checkedStores.includes(p.site.trim().toLowerCase());
        const matchesBrand = (p) => checkedBrands.length === 0 || checkedBrands.includes(getBrand(p).toUpperCase());
        const matchesPrice = (p) => {
            if (checkedPrices.length === 0) return true;
            const price = parseFloat(p.preco);
            if (isNaN(price)) return false;

            return checkedPrices.some(range => {
                const [min, max] = range.split('-').map(Number);
                if (max === 0) return price >= min;
                return price >= min && price <= max;
            });
        };

        const filtered = currentProducts.filter(p => matchesStore(p) && matchesBrand(p) && matchesPrice(p));
        renderProducts(filtered);

        // Atualizar contadores (Faceted Search)
        // O contador da categoria deve ignorar o próprio filtro para permitir multi-seleção
        const productsForBrands = currentProducts.filter(p => matchesStore(p) && matchesPrice(p));
        const productsForPrices = currentProducts.filter(p => matchesStore(p) && matchesBrand(p));
        const productsForStores = currentProducts.filter(p => matchesBrand(p) && matchesPrice(p));

        updateBrandFilters(productsForBrands, checkedBrands);
        updatePriceFilters(productsForPrices, checkedPrices);
        updateStoreFilters(productsForStores, checkedStores);
    }

    function getBrand(product) {
        if (product.marca) return product.marca.toUpperCase();

        const commonTerms = ['ar condicionado', 'geladeira', 'fogão', 'tv', 'smart', 'smartphone', 'celular', 'maquina de lavar', 'usado:', 'usado', 'maquina', 'lavadora'];
        let name = product.nome.toLowerCase();

        commonTerms.forEach(term => {
            name = name.replace(term, '').trim();
        });

        const words = name.split(/[\s,/-]+/).filter(w => w.length > 2);
        let brand = words[0] || 'OUTRO';
        return brand.toUpperCase();
    }

    function updateBrandFilters(products, activeBrands = []) {
        const brandCounts = {};
        products.forEach(p => {
            const brand = getBrand(p);
            brandCounts[brand] = (brandCounts[brand] || 0) + 1;
        });

        brandFiltersContainer.innerHTML = '';
        const sortedBrands = Object.keys(brandCounts).sort((a, b) => brandCounts[b] - brandCounts[a]);

        const finalBrands = [...new Set([...sortedBrands, ...activeBrands])];

        const renderBrand = (brand) => {
            const label = document.createElement('label');
            label.className = 'filter-option';
            const isChecked = activeBrands.includes(brand.toUpperCase());
            label.innerHTML = `
                <input type="checkbox" ${isChecked ? 'checked' : ''} value="${brand}"> ${brand} 
                <span class="count">(${brandCounts[brand] || 0})</span>
            `;
            label.querySelector('input').addEventListener('change', applyFilters);
            return label;
        };

        finalBrands.forEach(brand => brandFiltersContainer.appendChild(renderBrand(brand)));
    }

    function updateStoreFilters(products, activeStores = []) {
        const storeCounts = {};
        products.forEach(p => {
            storeCounts[p.site] = (storeCounts[p.site] || 0) + 1;
        });

        const allStores = [...new Set([...Object.keys(storeCounts), ...activeStores.map(s => currentProducts.find(p => p.site.toLowerCase() === s)?.site).filter(Boolean)])];

        storeFiltersContainer.innerHTML = '';
        allStores.forEach(store => {
            const label = document.createElement('label');
            label.className = 'filter-option';
            const isChecked = activeStores.includes(store.toLowerCase());
            label.innerHTML = `<input type="checkbox" ${isChecked ? 'checked' : ''} value="${store}"> ${store} <span class="count">(${storeCounts[store] || 0})</span>`;
            label.querySelector('input').addEventListener('change', applyFilters);
            storeFiltersContainer.appendChild(label);
        });
    }

    function updatePriceFilters(products, activePrices = []) {
        const priceFiltersContainer = document.getElementById('price-filters');
        if (!priceFiltersContainer) return;

        const ranges = [
            { label: 'R$ 0 - R$ 25', min: 0, max: 25 },
            { label: 'R$ 25 - R$ 50', min: 25, max: 50 },
            { label: 'R$ 50 - R$ 100', min: 50, max: 100 },
            { label: 'R$ 100 - R$ 250', min: 100, max: 250 },
            { label: 'R$ 250 - R$ 500', min: 250, max: 500 },
            { label: 'R$ 500 - R$ 1.000', min: 500, max: 1000 },
            { label: 'R$ 1.000 - R$ 2.500', min: 1000, max: 2500 },
            { label: 'R$ 2.500 - R$ 5.000', min: 2500, max: 5000 },
            { label: 'Acima de R$ 5.000', min: 5000, max: Infinity }
        ];

        const activeRanges = ranges.map(range => {
            const count = products.filter(p => {
                const price = parseFloat(p.preco);
                if (isNaN(price)) return false;
                return price >= range.min && (range.max === Infinity ? true : price <= range.max);
            }).length;
            range.count = count;
            return range;
        }).filter(range => range.count > 0 || activePrices.includes(`${range.min}-${range.max === Infinity ? 0 : range.max}`));

        priceFiltersContainer.innerHTML = '';

        const renderRange = (range) => {
            const label = document.createElement('label');
            label.className = 'filter-option';
            const value = `${range.min}-${range.max === Infinity ? 0 : range.max}`;
            const isChecked = activePrices.includes(value);
            label.innerHTML = `
                <input type="checkbox" name="price" ${isChecked ? 'checked' : ''} value="${value}"> ${range.label} 
                <span class="count">(${range.count})</span>
            `;
            label.querySelector('input').addEventListener('change', applyFilters);
            return label;
        };

        activeRanges.forEach(range => priceFiltersContainer.appendChild(renderRange(range)));
    }

    function sortProducts(products, type) {
        const sorted = [...products];
        if (type === 'price-asc') {
            return sorted.sort((a, b) => a.preco - b.preco);
        } else if (type === 'price-desc') {
            return sorted.sort((a, b) => b.preco - a.preco);
        }
        return sorted; // 'relevance' retorna original
    }

    // Inicialização: Busca produtos em destaque para a home
    async function initFeaturedProducts() {
        const featuredGrid = document.getElementById('featured-grid');
        if (!featuredGrid) return;

        featuredGrid.innerHTML = '<div class="loader"></div>';

        try {
            const response = await fetch(`/api/buscar/iphone`); // Exemplo de destaque
            const data = await response.json();

            if (data.sucesso && data.produtos.length > 0) {
                featuredGrid.innerHTML = '';
                // Mostra apenas os 4 primeiros no destaque
                renderToContainer(data.produtos.slice(0, 8), featuredGrid);
            } else {
                featuredGrid.innerHTML = '<p>Nenhuma oferta em destaque no momento.</p>';
            }
        } catch (error) {
            featuredGrid.innerHTML = '<p>Erro ao carregar destaques.</p>';
        }
    }

    function renderToContainer(products, container) {
        container.innerHTML = '';

        // Identifica o menor preço para colocar o selo
        const validPrices = products.filter(p => p.preco > 0).map(p => p.preco);
        const minPrice = validPrices.length > 0 ? Math.min(...validPrices) : null;

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'produto-card';

            const hasValidLink = product.link &&
                product.link !== 'null' &&
                product.link !== 'None' &&
                product.link !== '' &&
                product.link !== 'undefined';

            if (hasValidLink) {
                productCard.style.cursor = 'pointer';
                productCard.addEventListener('click', (e) => {
                    if (!e.target.closest('a')) {
                        window.open(product.link, '_blank');
                    }
                });
            }

            // Selo de Melhor Preço
            const isBestPrice = minPrice && product.preco === minPrice;
            const bestPriceBadge = isBestPrice ? `<div class="best-price-badge"><i class="fa-solid fa-tag"></i> Melhor Preço</div>` : '';

            const placeholderImage = "https://via.placeholder.com/250x250.png?text=Sem+Imagem";
            const imageUrl = product.imagem || placeholderImage;

            const imageHtml = hasValidLink
                ? `<div class="produto-imagem-container">
                     ${bestPriceBadge}
                     <a href="${product.link}" target="_blank"><img src="${imageUrl}" alt="${product.nome}" class="produto-imagem" onerror="this.onerror=null;this.src='${placeholderImage}';"></a>
                   </div>`
                : `<div class="produto-imagem-container">
                     ${bestPriceBadge}
                     <img src="${imageUrl}" alt="${product.nome}" class="produto-imagem" onerror="this.onerror=null;this.src='${placeholderImage}';">
                   </div>`;

            const linkButton = hasValidLink
                ? `<a href="${product.link}" target="_blank" class="produto-link">Ver na Loja →</a>`
                : `<div class="produto-link-disabled">Link indisponível</div>`;

            productCard.innerHTML = `
                ${imageHtml}
                <div class="card-content">
                    <div class="produto-site">${product.site}</div>
                    <div class="produto-nome">${product.nome}</div>
                    <div class="produto-preco">${product.preco_formatado || `R$ ${Number(product.preco).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}</div>
                </div>
                ${linkButton}
            `;
            container.appendChild(productCard);
        });
    }

    function renderProducts(products) {
        renderToContainer(products, resultsGrid);
    }

    initFeaturedProducts();
});