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
    alignItems: "flex-end",
    justifyContent: "center",
    gap: 8,
  },
  statusPagamento: {
    color: "#F97316",
    fontWeight: "bold",
    fontSize: 13,
  },
  botaoFinalizarDevolucao: {
    backgroundColor: "#1e2d52",
    borderWidth: 1,
    borderColor: "#0d3468",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6
  },
  textoBotaoFinalizar: {
    color: "#E6EDF3",
    fontWeight: "600"
  }
});
