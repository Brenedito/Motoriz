import axios, { AxiosResponse } from "axios";
import { Veiculo } from './../screens/DashboardVeiculos';

const api = axios.create({
    baseURL: 'http://localhost:8080/api',
    timeout: 5000,
})

export const getVeiculos = (): Promise<AxiosResponse<Veiculo[]>> => {
    return api.get<Veiculo[]>('/veiculos');
};
export const getVeiculoById = (id: string | number): Promise<AxiosResponse<Veiculo>> => {
    return api.get<Veiculo>(`/veiculos/${id}`)
};
export const getVeiculoByStatus = (status: Veiculo['status']): Promise<AxiosResponse<Veiculo[]>> => {
    return api.get<Veiculo[]>(`/veiculos/status/${status}`)
};