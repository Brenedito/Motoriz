import {
  FlatList,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle,
} from "react-native";
import { styles } from "../styles/DocumentosStyle";
import { useMemo, useState } from "react";

type statusPagamento =
  | "PENDENTE"
  | "PAGO"
  | "ATRASADO"
  | "RECUSADO"
  | "CANCELADO";

interface ContratoDoVeiculo {
  id: string;
  modelo: string;
  placa: string;
  valor: number;
  statusPagamento: statusPagamento;
  vencimento: string;
  cliente: string;
}

interface StatusConfig {
  label: string;
  style: TextStyle | ViewStyle;
}

const contratosExemplo: ContratoDoVeiculo[] = [
  {
    id: "1",
    modelo: "Chevrolet Onix",
    placa: "ABC-1234",
    valor: 150.0,
    statusPagamento: "PENDENTE",
    vencimento: "15-05-2027",
    cliente: "João Costa",
  },
  {
    id: "2",
    modelo: "Toyota Prius",
    placa: "XYZ-5678",
    valor: 200.0,
    statusPagamento: "PAGO",
    vencimento: "20-05-2027",
    cliente: "Maria Silva",
  },
];

export function Documentos() {
  const [contratosAtivos, setContratosAtivos] = useState<ContratoDoVeiculo[]>(
    [],
  );

  const numeroDeContratos = useMemo(() => {
    const totalContratos = contratosExemplo.length;
    return totalContratos;
  }, [contratosAtivos]);
  return (
    <View style={styles.container}>
      <View style={styles.headerListaDeContratos}>
        <View style={styles.containerDocumentos}>
          <Text style={styles.headerListaDeContatosTexto}>
            Contratos Ativos
          </Text>
          <Text style={styles.headerListaDeContatosDescricao}>
            Veja contratos atuais e finalize devoluções
          </Text>
        </View>

        <Text style={styles.numeroDeContratos}>{numeroDeContratos} Ativos</Text>
      </View>
      <View style={styles.containerListaDeContratos}>
        
          <FlatList
            data={contratosExemplo}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => {
              return (
                <View style={styles.listaDeContratosCard}>
                  <View style={styles.contratosInfo}>
                    <View style={styles.tituloContrato}>
                      <Text style={styles.textoCliente}>{item.cliente}</Text>
                      <Text style={styles.textoPlaca}>{item.placa}</Text>
                    </View>
                    <View style={styles.descricaoContrato}>
                      <Text style={styles.textoModelo}>{item.modelo}</Text>
                      <Text style={styles.textoValor}>R$ {item.valor}</Text>
                      <Text style={styles.textoVencimento}>
                        Vencimento: {item.vencimento}
                      </Text>
                    </View>
                  </View>
                  <View style={styles.statusEBotaoFevolucao}>
                    <Text style={styles.statusPagamento}>
                      {item.statusPagamento}
                    </Text>
                    <TouchableOpacity style={styles.botaoFinalizarDevolucao}>
                      <Text style={styles.textoBotaoFinalizar}>Finalizar Devolução</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            }}
          />
      </View>
    </View>
  );
}
