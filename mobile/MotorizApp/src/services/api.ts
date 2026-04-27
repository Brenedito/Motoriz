import axios, { AxiosResponse } from "axios";
import { Veiculo } from './../screens/DashboardVeiculos';

const api = axios.create({
    baseURL: 'http://localhost:8080/api',
})

export const getVeiculos = (): Promise<AxiosResponse<Veiculo[]>> => {
    return api.get('/veiculos');
};
export const getVeiculoById = (id: number): Promise<AxiosResponse<Veiculo[]>> => {
    return api.get(`/veiculos/${id}`)
};
export const getVeiculoByStatus = (status: Veiculo['status']): Promise<AxiosResponse<Veiculo[]>> => {
    return api.get(`/veiculos/status/${status}`)
};