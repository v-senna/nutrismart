"use client";

import { useState, useMemo, useEffect } from "react";
import { X, ShoppingCart, MapPin, Plus, Trash2, Calculator, Info, Download, Printer, Package } from "lucide-react";
import styles from "./ShoppingListModal.module.css";

interface ShoppingListModalProps {
  onClose: () => void;
  meals: any[];
}

const REGIONAL_MULTIPLIERS: Record<string, { label: string, factor: number }> = {
  "araras_copacabana": { label: "Araras/SP (Ref: SM Copacabana)", factor: 1.0 },
  "sudeste": { label: "Sudeste (SP, RJ, MG, ES)", factor: 1.1 },
  "sul": { label: "Sul (PR, SC, RS)", factor: 1.05 },
  "nordeste": { label: "Nordeste (BA, CE, PE, etc)", factor: 0.95 },
  "centro-oeste": { label: "Centro-Oeste (DF, GO, MT, MS)", factor: 1.0 },
  "norte": { label: "Norte (AM, PA, RR, etc)", factor: 1.2 },
};

const BRAZIL_STATES = [
  { sigla: 'AC', nome: 'Acre' }, { sigla: 'AL', nome: 'Alagoas' }, { sigla: 'AP', nome: 'Amapá' },
  { sigla: 'AM', nome: 'Amazonas' }, { sigla: 'BA', nome: 'Bahia' }, { sigla: 'CE', nome: 'Ceará' },
  { sigla: 'DF', nome: 'Distrito Federal' }, { sigla: 'ES', nome: 'Espírito Santo' }, { sigla: 'GO', nome: 'Goiás' },
  { sigla: 'MA', nome: 'Maranhão' }, { sigla: 'MT', nome: 'Mato Grosso' }, { sigla: 'MS', nome: 'Mato Grosso do Sul' },
  { sigla: 'MG', nome: 'Minas Gerais' }, { sigla: 'PA', nome: 'Pará' }, { sigla: 'PB', nome: 'Paraíba' },
  { sigla: 'PR', nome: 'Paraná' }, { sigla: 'PE', nome: 'Pernambuco' }, { sigla: 'PI', nome: 'Piauí' },
  { sigla: 'RJ', nome: 'Rio de Janeiro' }, { sigla: 'RN', nome: 'Rio Grande do Norte' }, { sigla: 'RS', nome: 'Rio Grande do Sul' },
  { sigla: 'RO', nome: 'Rondônia' }, { sigla: 'RR', nome: 'Roraima' }, { sigla: 'SC', nome: 'Santa Catarina' },
  { sigla: 'SP', nome: 'São Paulo' }, { sigla: 'SE', nome: 'Sergipe' }, { sigla: 'TO', nome: 'Tocantins' }
];

import { fetchApi } from "@/lib/api";

export default function ShoppingListModal({ onClose, meals }: ShoppingListModalProps) {
  const [region, setRegion] = useState("araras_copacabana");
  const [selectedState, setSelectedState] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  const [cities, setCities] = useState<{nome: string}[]>([]);
  const [supermarkets, setSupermarkets] = useState<{name: string, url: string}[]>([]);
  const [selectedSupermarket, setSelectedSupermarket] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isQuoting, setIsQuoting] = useState(false);
  const [animate, setAnimate] = useState(false);
  
  useEffect(() => {
    setAnimate(true);
  }, []);

  useEffect(() => {
    if (selectedState) {
      fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${selectedState}/municipios`)
        .then(res => res.json())
        .then(data => {
          setCities(data.sort((a: any, b: any) => a.nome.localeCompare(b.nome)));
          setSelectedCity("");
          setSupermarkets([]);
          setSelectedSupermarket("");
        })
        .catch(err => console.error("Erro ao buscar cidades:", err));
    } else {
      setCities([]);
    }
  }, [selectedState]);

  // Extrair itens das sugestões de refeições de forma mais robusta
  const initialItems = useMemo(() => {
    const items: { name: string; quantity: number; unit: string; basePrice: number; category: string }[] = [];
    const seen = new Map<string, number>();

    const categories: Record<string, string[]> = {
      "Proteínas": ["frango", "carne", "ovo", "peixe", "whey", "leite", "iogurte", "queijo", "patinho", "tilápia", "omelete"],
      "Carboidratos": ["arroz", "feijão", "batata", "pão", "aveia", "macarrão", "tapioca", "banana", "fruta", "mamão", "pera", "maçã"],
      "Gorduras / Outros": ["azeite", "castanha", "abacate", "pasta de amendoim", "salada", "legumes", "amendoim"]
    };

    meals.forEach(meal => {
      const suggestion = meal.suggestion;
      const parts = suggestion.split(/[,+]| e | com /);
      
      parts.forEach((p: string) => {
        let text = p.trim().toLowerCase();
        
        // Tentar extrair quantidade numérica
        const qtyMatch = text.match(/^(\d+[,.]?\d*)\s*(g|ml|und|unidades|colher|fatia|scop|scoop|un)s?\s*(de)?\s*(.*)/i);
        
        let qty = 1;
        let unit = "un";
        let name = text;

        if (qtyMatch) {
          qty = parseFloat(qtyMatch[1].replace(',', '.'));
          unit = qtyMatch[2];
          name = qtyMatch[4].trim();
        } else {
          // Fallback para nomes sem quantidade explícita no início
          name = text.replace(/^\d+\s*/, "");
        }

        if (name && name.length > 2) {
          if (seen.has(name)) {
             // Se já viu esse item, soma a quantidade (aproximação para a semana)
             const existingIdx = items.findIndex(item => item.name.toLowerCase() === name);
             if (existingIdx !== -1) {
                items[existingIdx].quantity += qty * 7; // Multiplica por 7 para a semana
             }
          } else {
            seen.set(name, items.length);
            
            let category = "Gorduras / Outros";
            for (const [cat, keywords] of Object.entries(categories)) {
              if (keywords.some(k => name.includes(k))) {
                category = cat;
                break;
              }
            }

            // Preço base estimado por UNIDADE/MEDIDA
            let basePrice = 5.0;
            if (category === "Proteínas") basePrice = 15.0;
            if (category === "Carboidratos") basePrice = 4.0;

            items.push({ 
              name: name.charAt(0).toUpperCase() + name.slice(1), 
              quantity: qty * 7, // Estimativa semanal
              unit: unit,
              basePrice,
              category
            });
          }
        }
      });
    });

    // Post-process items to intelligent purchase units
    const processedItems = items.map(item => {
      let finalQty = item.quantity;
      let finalUnit = item.unit.toLowerCase().replace(/s$/, ""); // singularize
      let finalBasePrice = item.basePrice;

      const lowerName = item.name.toLowerCase();

      // Whey Protein -> Pote (~30 scoops/porções)
      if (lowerName.includes("whey") || lowerName.includes("creatina")) {
         finalUnit = "pote";
         // Assumimos que a quantidade original era scoop ou un, 1 pote dura ~30
         finalQty = Math.ceil(item.quantity / 30) || 1;
         finalBasePrice = lowerName.includes("creatina") ? 89.90 : 139.90; // Ref: Média Suplementos
      } 
      // Ovos -> Cartela de 30 (Referência Supermercado)
      else if (lowerName.includes("ovo") || lowerName.includes("omelete")) {
         finalUnit = "cartela (30un)";
         finalQty = Math.ceil(item.quantity / 30) || 1; // 1 cartela a cada 30 ovos
         finalBasePrice = 21.90; // Ref: Cartela 30 ovos SM Copacabana
      }
      // Itens comuns em gramas -> Kg
      else if (['g', 'grama'].includes(finalUnit) || ['frango', 'carne', 'patinho', 'peixe', 'tilápia', 'mignon'].some(k => lowerName.includes(k))) {
          if (['g', 'grama'].includes(finalUnit)) {
              finalUnit = "kg";
              finalQty = item.quantity / 1000;
          } else if (['colher', 'escumadeira'].some(u => finalUnit.includes(u))) {
              finalUnit = "kg";
              finalQty = (item.quantity * 25) / 1000; // Estima 25g por colher
          } else {
              // Fallback se for 'un' mas for carne
              finalUnit = "kg";
              finalQty = (item.quantity * 150) / 1000; // Estima 150g por 'unidade' (ex: 1 bife)
          }
          
          if (lowerName.includes("frango")) finalBasePrice = 19.90; // Ref: Filé de Peito Frango
          else if (['mignon'].some(k => lowerName.includes(k))) finalBasePrice = 69.90; // Ref: Mignon
          else if (['carne', 'patinho'].some(k => lowerName.includes(k))) finalBasePrice = 38.90; // Ref: Patinho Moído
          else if (['peixe', 'tilápia'].some(k => lowerName.includes(k))) finalBasePrice = 49.90; // Ref: Tilápia
          else if (['arroz'].some(k => lowerName.includes(k))) finalBasePrice = 5.40; // Ref: Arroz pct 5kg (27.00/5)
          else if (['feijão'].some(k => lowerName.includes(k))) finalBasePrice = 7.90; // Ref: Feijão Carioca
          else finalBasePrice = 15.90;
      }
      // Pão -> Pacote (pct)
      else if (lowerName.includes("pão")) {
          finalUnit = "pct";
          finalQty = Math.ceil(item.quantity / 15) || 1; // 15 fatias por pct
          finalBasePrice = 10.0;
      }
      // Frutas e Vegetais
      else if (['banana', 'maçã', 'pera', 'laranja'].some(k => lowerName.includes(k))) {
          finalUnit = "dz";
          finalQty = Math.ceil(item.quantity / 12) || 1;
          finalBasePrice = 15.0;
      }
      // Padronizar 'un'
      else {
          if (['colher', 'fatia', 'und', 'unidade', 'un'].includes(finalUnit)) {
              finalUnit = "un";
          }
      }

      return {
          ...item,
          quantity: Number(finalQty.toFixed(1)) || 1, // Garantir pelo menos 1
          unit: finalUnit,
          basePrice: finalBasePrice
      };
    });

    return processedItems;
  }, [meals]);

  const [items, setItems] = useState(initialItems);

  const updateQuantity = (index: number, newQty: number) => {
    const newItems = [...items];
    newItems[index].quantity = newQty;
    setItems(newItems);
  };

  const multiplier = REGIONAL_MULTIPLIERS[region]?.factor || 1.0;

  const total = items.reduce((acc, item) => acc + (item.basePrice * item.quantity * multiplier), 0);

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updatePrice = (index: number, newPrice: number) => {
    const newItems = [...items];
    newItems[index].basePrice = newPrice;
    setItems(newItems);
  };

  const handlePrint = () => {
    document.body.classList.add("printing-active");
    window.print();
    setTimeout(() => {
        document.body.classList.remove("printing-active");
    }, 500);
  };

  const handleSearchSupermarkets = async () => {
    if (!selectedState || !selectedCity) return;
    setIsSearching(true);
    const searchRegion = `${selectedCity}, ${selectedState}`;
    try {
      const token = localStorage.getItem("token");
      const res = await fetchApi("/search-supermarkets", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({ region: searchRegion })
      });
      setSupermarkets(res || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  };

  const handleQuoteList = async () => {
    if (!selectedSupermarket) return;
    setIsQuoting(true);
    try {
      const token = localStorage.getItem("token");
      const itemNames = items.map(i => i.name);
      const searchRegion = `${selectedCity}, ${selectedState}`;
      const res = await fetchApi("/quote-shopping-list", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({ items: itemNames, supermarket: selectedSupermarket, region: searchRegion })
      });
      if (res && Array.isArray(res)) {
        const newItems = [...items];
        res.forEach(quoted => {
          const idx = newItems.findIndex(i => i.name === quoted.item);
          if (idx !== -1) {
            newItems[idx].basePrice = quoted.price;
          }
        });
        setItems(newItems);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsQuoting(false);
    }
  };

  return (
    <div className={`${styles.overlay} ${animate ? styles.active : ""} printable-area`}>
      <div className={`glass-card ${styles.modal} print-modal`}>
        <button className={`${styles.closeBtn} print-hide`} onClick={onClose}><X size={24} /></button>
        
        <div className={styles.header}>
          <div className={styles.titleIcon}>
            <ShoppingCart size={28} className="text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-primary">Lista de Compras Inteligente</h2>
            <p className="text-xs text-muted">Gerada para 7 dias com base no seu cardápio</p>
          </div>
        </div>

        <div className={styles.configBar}>
          <div className={styles.configItem} style={{ flex: 1 }}>
            <label><MapPin size={14} /> Selecione sua Região para Buscar Supermercados</label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <select 
                className={styles.select}
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                style={{ flex: 1, minWidth: '100px' }}
              >
                <option value="">Estado</option>
                {BRAZIL_STATES.map((st) => (
                  <option key={st.sigla} value={st.sigla}>{st.sigla}</option>
                ))}
              </select>

              <select 
                className={styles.select}
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                disabled={!selectedState}
                style={{ flex: 2, minWidth: '150px' }}
              >
                <option value="">Cidade</option>
                {cities.map((city) => (
                  <option key={city.nome} value={city.nome}>{city.nome}</option>
                ))}
              </select>

              <button 
                onClick={handleSearchSupermarkets} 
                className="btn btn-primary" 
                style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                disabled={isSearching || !selectedCity}
              >
                {isSearching ? "Buscando..." : "Buscar Mercados"}
              </button>
            </div>
            
            {supermarkets.length > 0 && (
              <div style={{ marginTop: '0.5rem' }}>
                <label className="text-xs text-muted">Selecione o Supermercado Base:</label>
                <select 
                  className={styles.select}
                  value={selectedSupermarket}
                  onChange={(e) => setSelectedSupermarket(e.target.value)}
                  style={{ marginTop: '0.25rem' }}
                >
                  <option value="">Escolha um mercado...</option>
                  {supermarkets.map((sm, i) => (
                    <option key={i} value={sm.name}>{sm.name}</option>
                  ))}
                </select>
                {selectedSupermarket && (
                  <button 
                    onClick={handleQuoteList}
                    className="btn"
                    style={{ background: 'var(--primary)', color: 'black', marginTop: '0.5rem', width: '100%', fontSize: '0.85rem' }}
                    disabled={isQuoting}
                  >
                    {isQuoting ? "Cotando..." : "Cotar Preços Reais via IA"}
                  </button>
                )}
              </div>
            )}
          </div>

          <div className={styles.summaryBadge}>
            <span className="text-[10px] uppercase tracking-wider opacity-60">Total Estimado (Semana)</span>
            <span className="text-lg font-bold text-primary">R$ {total.toFixed(2)}</span>
          </div>
        </div>

        <div className={styles.listContainer}>
          {Object.entries(items.reduce((acc, item) => {
            if (!acc[item.category]) acc[item.category] = [];
            acc[item.category].push(item);
            return acc;
          }, {} as Record<string, typeof items>)).map(([category, catItems]) => (
            <div key={category} className={styles.categorySection}>
              <h3 className={styles.categoryTitle}>{category}</h3>
              <div className={styles.itemsGrid}>
                {catItems.map((item, idx) => {
                  const globalIdx = items.indexOf(item);
                  return (
                    <div key={globalIdx} className={styles.itemCard}>
                      <div className={styles.itemInfo}>
                        <span className={styles.itemName}>{item.name}</span>
                        {/* Preço agora mais discreto */}
                        <div className={styles.qtyInputWrap}>
                          <span className="text-[10px] text-muted mr-1">R$</span>
                          <input 
                            type="number" 
                            step="0.5"
                            className={styles.qtyInput}
                            style={{ width: '40px' }}
                            value={item.basePrice}
                            onChange={(e) => updatePrice(globalIdx, parseFloat(e.target.value) || 0)}
                          />
                          <span className="text-[10px] text-muted ml-1">/{item.unit}</span>
                        </div>
                      </div>
                      <div className={styles.itemPriceActions}>
                        {/* Quantidade agora no box cinza de destaque */}
                        <div className={styles.priceInputWrap}>
                            <input 
                                type="number" 
                                step={["pote", "dz", "pct", "un"].includes(item.unit) ? "1" : "0.1"}
                                className={styles.priceInput}
                                value={item.quantity}
                                onChange={(e) => updateQuantity(globalIdx, parseFloat(e.target.value) || 0)}
                            />
                            <span className="text-[11px] font-bold text-muted ml-1">{item.unit}</span>
                        </div>
                        <div className={styles.subtotal}>
                          R$ {(item.basePrice * item.quantity * multiplier).toFixed(2)}
                        </div>
                        <button onClick={() => removeItem(globalIdx)} className={`${styles.removeBtn} print-hide`}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
          
          {items.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-muted">
              <ShoppingCart size={48} className="opacity-20 mb-4" />
              <p>Sua lista está vazia.</p>
            </div>
          )}
        </div>

        <div className={`${styles.footer} print-footer`}>
          <div className={styles.infoNote}>
            <Info size={14} />
            <span>Os preços variam conforme a quantidade semanal. Ajuste conforme necessário.</span>
          </div>
          <div className={`${styles.actions} print-hide`}>
            <button className={`${styles.actionBtn} ${styles.outline}`} onClick={handlePrint}>
              <Printer size={18} /> Imprimir / PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
