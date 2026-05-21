import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0F172A',
        alignItems: 'center',
    },
    headerListaDeContratos: {
        flexDirection: 'row',
        width: '100%'
    },
    containerListaDeContratos: {
        flexDirection: 'column',
        padding: 18,
    },
    headerListaDeContatosTexto: {
        color: '#fff',
        fontSize: 22,
        fontWeight: '800',
        marginBottom: 6
    },
    headerListaDeContatosDescricao: {
        color: '#83898f',
        fontSize: 14,
    },
    numeroDeContratos: {
        backgroundColor: '#22c55e4d',
        color: '#22C55E',
        height: 24,
        marginTop: 26,
        paddingHorizontal: 6,
        borderRadius: 12,
        textAlign: 'center',
        fontSize: 15,
        fontWeight: '600',
        marginLeft: -10,
    },
    listaDeContratos: {

    }
}) 