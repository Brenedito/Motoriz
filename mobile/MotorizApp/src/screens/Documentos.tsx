import { FlatList, Text, View } from "react-native";
import { styles } from "../styles/DocumentosStyle";
import { useMemo, useState } from "react";

type statusPagamento = "PENDENTE" | "PAGO" | "ATRASADO" | "RECUSADO" |     "CANCELADO";

interface ContratoDoVeiculo {
  id: string;
  modelo: string;
  placa: string;
  valor: number;
  statusPagamento: statusPagamento;
  vencimento: string;
  cliente: string;
}

export function Documentos() {
  const [contratosAtivos, setContratosAtivos] = useState<ContratoDoVeiculo[]>([]);

  const numeroDeContratos = useMemo(() => {
    const totalContratos = contratosAtivos.length;
    return totalContratos
  }, [contratosAtivos]);
  return (
    <View style={styles.container}>
      <View style={styles.headerListaDeContratos}>
        <View style={styles.containerListaDeContratos}>
          <Text style={styles.headerListaDeContatosTexto}>
            Contratos Ativos
          </Text>
          <Text style={styles.headerListaDeContatosDescricao}>
            Veja contratos atuais e finalize devoluções
          </Text>
        </View>

        <Text style={styles.numeroDeContratos}>{numeroDeContratos} Ativos</Text>
      </View>
      <View style={styles.listaDeContratos}>
        <FlatList
          data={contratosAtivos}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => {
            return (
              <View>

              </View>
            )
          }}
        />
      </View>
    </View>
  );
}
