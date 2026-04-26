import axios from "axios";

const api = axios.create({
    baseURL: 'http://localhost:8080/api',
})

export const getVeiculos = () => api.get('/veiculos');
export const getVeiculoById = (id: number) => api.get(`/veiculos/${id}`);
export const getVeiculoByStatus = (status: string) => api.get(`/veiculos/status/${status}`);