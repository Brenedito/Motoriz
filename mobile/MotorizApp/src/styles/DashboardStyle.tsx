import { StyleSheet } from 'react-native';
import { Colors } from './Colors';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
  },
  navbar: {
    flexDirection: 'row',
    width: '100%',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    alignItems: 'center',
    backgroundColor: Colors.primary,
  },
  appTitle: {
    fontSize: 20,
    fontWeight: '500',
    color: '#FFF',
  },
  header: {
    padding: 16,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#fff',
    marginBottom: 16,
  },
  containerInfos: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  infoCard: {
    width: '48%',
    backgroundColor: Colors.primary,
    borderRadius: 14,
    borderWidth: 1,
    padding: 14,
    borderColor: Colors.border,
  },
  cardLabel: {
    fontSize: 12.5,
    color: Colors.textMuted,
    fontWeight: '600',
  },
  cardValue: {
    fontSize: 30,
    fontWeight: '800',
    color: Colors.textMain,
  },
  cardDescription: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  veiculosContainer: {
    padding: 14,
    backgroundColor: Colors.primary,
    width: '90%',
    borderRadius: 8,
  },
  veiculosHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 1000,
    // marginTop: 6,
    // marginBottom: 17,
  },
  veiculosHeaderTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#fff',
    marginRight: 65,
  },
  dropdownFiltrar: {
    position: 'relative',
    minWidth: 100,
    marginRight: 30
  },
  textoSelecionado: {
    fontSize: 14,
    color: Colors.textMain,
    fontWeight: 'bold',
    marginLeft: 3
  },
  seta: {
    fontSize: 12,
    color: Colors.textMain,
    marginLeft: 6,
  },
  botaoSelecao: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingVertical: 3,
    paddingHorizontal: 'auto',
    width: 'auto',
    backgroundColor: '#882c2c00',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#ccc',
  },
  opcoesDropdown: {
    position: 'absolute',
    top: '110%',
    right: 0,
    backgroundColor: Colors.primary,
    borderRadius: 10,
    minWidth: 100,
    color: Colors.textMain,
    elevation: 5,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
  },
  opcaoItem: {
    padding: 6,
    borderBottomWidth: 1,
  },
  opcaoSelecionada: {
    backgroundColor: '#1d478b',
    color: Colors.textMain
  },
  textoOpcaoAtiva: {
    color: Colors.primary,
    fontWeight: 'bold',
  },
  filtrarButton: {
    backgroundColor: '#334155',
  },
  filtrarButtonAtivo: {

  },
  veiculosList: {
    alignItems: 'center',
    fontSize: 14,
    color: '#b8bfc7',
    marginBottom: 12,
    width: '100%',
  },
  veiculosCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: Colors.cardBackground,
    borderRadius: 10,
    paddingHorizontal: 18,
    paddingVertical: 10,
    marginBottom: 10,
    width: '100%',
    borderWidth: 1,
    borderColor: '#0b2b55',
  },
  veiculosInfo: {
    marginVertical: 4,
  },
  veiculosModelo: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    fontSize: 14,
    color: Colors.textMain,
    fontWeight: '600',
    marginVertical: 5,
  },
  veiculosPlaca: {
    fontSize: 14,
    color: Colors.textMain,
    backgroundColor: '#334155',
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignSelf: 'flex-start',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 4,
  },
  veiculosKm: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  statusAndButtonLocalizar: {
    flexDirection: 'column',
    alignItems: 'center',
  },
  veiculosStatus: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.success,
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  buttonLocalizar: {
    marginTop: 27,
    backgroundColor: '#334155',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  Localizar: {
    fontSize: 14,
    color: Colors.textMain,
  },
  footerVerMaisVeiculos: {
    padding: 12,
    alignItems: 'center',
  },
  verMaisVeiculos: {
    color: Colors.success,
    fontSize: 14,
    fontWeight: '600',
    marginVertical: 10,
  },
  statusDisponivel: {
    backgroundColor: '#22c55e26',
    color: '#22C55E'
  },
  statusAlugado: {
    color: '#3B82F6',
    backgroundColor: '#3b82f626'
  }, 
  statusManutencao: {
    backgroundColor: '#f59e0b26',
    color: '#F59E0B',
  }
});
