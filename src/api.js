import axios from 'axios';

const API_URL = 'https://minutas-backend-production.up.railway.app';

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

export const getProyectos = () =>
  api.get('/proyectos/').then(r => r.data);

export const getContratos = (params = {}) =>
  api.get('/contratos/', { params }).then(r => r.data);

export const crearContrato = (data) =>
  api.post('/contratos/', data).then(r => r.data);

export const actualizarContrato = (id, data) =>
  api.put(`/contratos/${id}`, data).then(r => r.data);

export const getManzanas = (proyecto_id) =>
  api.get('/lotes/manzanas', { params: { proyecto_id } }).then(r => r.data);

export const getLotes = (proyecto_id, manzana) =>
  api.get('/lotes/', { params: { proyecto_id, manzana } }).then(r => r.data);

export const getRegiones = () =>
  api.get('/distritos/regiones').then(r => r.data);

export const getProvincias = (region) =>
  api.get(`/distritos/provincias/${encodeURIComponent(region)}`).then(r => r.data);

export const getDistritos = (region, provincia) =>
  api.get(`/distritos/distritos/${encodeURIComponent(region)}/${encodeURIComponent(provincia)}`).then(r => r.data);

export const getMinutaUrl = (id) =>
  `${API_URL}/minutas/descargar/${id}`;

export default api;
