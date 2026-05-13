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
    marginLeft: 5,
    marginBottom: 17,
  },
  veiculosHeaderTitle: {
    position: 'static',
    fontSize: 18,
    fontWeight: '800',
    color: '#fff',
    flex: 1,
  },
  dropdownFiltrar: {
    position: 'relative',
    minWidth: 100,
    alignItems: 'flex-end',
    zIndex: 1001,
  },
  textoSelecionado: {
    fontSize: 14,
    color: Colors.textMain,
    fontWeight: 'bold',
    marginHorizontal: 4
  },
  botaoSelecao: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingVertical: 6,
    paddingHorizontal: 8,
    backgroundColor: Colors.cardBackground,
    borderRadius: 8,
    borderColor: '#ccc',
    minWidth: 110,
  },
  opcoesDropdown: {
    position: 'absolute',
    top: '115%',
    right: 0,
    backgroundColor: Colors.cardBackground,
    borderRadius: 10,
    minWidth: 140,
    elevation: 10,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    overflow: 'scroll',
  },
  opcaoItem: {
    padding: 5,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  opcaoItemContent: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    width: '100%',
    paddingHorizontal: 12,
    height: 20,
  },
  opcaoItemText: {
    flexDirection: 'row',
    fontSize: 12,
    fontWeight: '500',
    color: Colors.textMain
  },
  opcaoSelecionada: {
    backgroundColor: '#1d478b',
    color: Colors.textMain
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
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 27,
    backgroundColor: '#334155',
    width: 100,
    gap: 3,
    paddingHorizontal: 5,
    paddingVertical: 3,
    borderRadius: 8,
  },
  Localizar: {
    fontSize: 12,
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
