import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0F172A",
    alignItems: "center",
  },
  headerListaDeContratos: {
    flexDirection: 'row',
    width: "100%",
    justifyContent: "space-between",
    paddingRight: 18,
  },
  containerDocumentos: {
    flexDirection: "column",
    padding: 18,
  },
  headerListaDeContatosTexto: {
    color: "#fff",
    fontSize: 22,
    fontWeight: "800",
    marginBottom: 6,
  },
  headerListaDeContatosDescricao: {
    color: "#83898f",
    fontSize: 14,
  },
  numeroDeContratos: {
    backgroundColor: "#22c55e2f",
    color: "#22C55E",
    height: 28,
    marginTop: 26,
    paddingHorizontal: 10,
    paddingTop: 4,
    borderRadius: 12,
    textAlign: "center",
    fontSize: 14,
    fontWeight: "600",
  },
  containerListaDeContratos: {
    backgroundColor: "#192f53",
    padding: 14,
    width: "95%",
    borderRadius: 8,
    marginTop: 20,
  },
  listaDeContratosCard: {
    backgroundColor: '#1E293B',
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderRadius: 10,
    paddingHorizontal: 15,
    paddingVertical: 12,
    marginBottom: 10,
    width: '100%',
    alignItems: "center"
  },
  contratosInfo: {
    flexDirection: 'column',
    flex: 1,
  },
  tituloContrato: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
    gap: 8,
  },
  textoCliente: {
    color: '#fff',
    fontSize: 16,
    fontWeight: "600",
  },
  textoPlaca: {
    color: '#fff',
    backgroundColor: '#334155',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    fontSize: 12,
    overflow: 'hidden',
  },
  descricaoContrato: {
    flexDirection: "column",
    gap: 2,
  },
  textoModelo: {
    color: '#83898f',
    fontSize: 14,
  },
  textoValor: {
    color: '#83898f',
    fontSize: 14,
  },
  textoVencimento: {
    color: '#EF4444',
    fontWeight: '600',
    fontSize: 13,
  },
  statusEBotaoFevolucao: {
    flexDirection: 'column',
    alignItems: 'flex-end',
  },
  statusPagamento: {
    color: "#F97316",
    fontWeight: "600",
    fontSize: 13,
    alignItems: 'flex-end',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  botaoFinalizarDevolucao: {
    backgroundColor: "#334155",
    marginTop: 27,
    gap: 3,
    borderWidth: 1,
    borderColor: 'transparent',
    paddingHorizontal: 6,
    paddingVertical: 4,
    borderRadius: 8
  },
  textoBotaoFinalizar: {
    color: "#E6EDF3",
    fontWeight: "600",
    fontSize: 14,
  },
  statusPendente: {
    color: "#F97316",
    backgroundColor: '#f59e0b26',
  },
  statusPago: {
    color: "#22C55E",
    backgroundColor: '#22c55e26',
  },
  statusAtrasado: {
    color: "#EF4444",
    backgroundColor: '#ef444426',
  },
  statusRecusado: {
    color: "#EF4444",
    backgroundColor: '#ef444426',
  },
  statusCancelado: {
    color: "#EF4444",
    backgroundColor: '#ef444426',
  },
});
