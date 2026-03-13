import { useEffect, useState, useCallback } from 'react';
import {
  View, Text, FlatList, TextInput, TouchableOpacity,
  StyleSheet, ActivityIndicator, RefreshControl, Alert, Modal
} from 'react-native';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { getProyectos, getContratos, getMinutaUrl } from '../src/api';
import { useProyecto } from './_layout';

const COLORES = {
  VERDE:    { bg: '#dcfce7', border: '#16a34a', text: '#15803d' },
  AMARILLO: { bg: '#fef9c3', border: '#ca8a04', text: '#a16207' },
  AZUL:     { bg: '#dbeafe', border: '#2563eb', text: '#1d4ed8' },
  ROJO:     { bg: '#fee2e2', border: '#dc2626', text: '#b91c1c' },
};

const FILTROS = ['TODOS', 'VERDE', 'AMARILLO', 'AZUL', 'ROJO'];

const ICONOS_PROYECTO = ['🏖️', '🏡', '🌿'];

export default function Contratos() {
  const { proyecto, setProyecto } = useProyecto();
  const [proyectos, setProyectos]     = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [contratos, setContratos]     = useState([]);
  const [loading, setLoading]         = useState(false);
  const [refreshing, setRefreshing]   = useState(false);
  const [busqueda, setBusqueda]       = useState('');
  const [filtro, setFiltro]           = useState('TODOS');
  const [descargando, setDescargando] = useState(null);

  // Cargar proyectos al inicio
  useEffect(() => {
    getProyectos()
      .then(data => {
        setProyectos(data);
        if (!proyecto && data.length > 0) setModalVisible(true);
      })
      .catch(() => Alert.alert('Error', 'No se pudo conectar al servidor'));
  }, []);

  const cargar = useCallback(async () => {
    if (!proyecto) return;
    setLoading(true);
    try {
      const params = { proyecto_id: proyecto.id };
      if (busqueda) params.busqueda = busqueda;
      if (filtro !== 'TODOS') params.estado = filtro;
      const data = await getContratos(params);
      setContratos(data);
    } catch {
      Alert.alert('Error', 'No se pudo cargar los contratos');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [proyecto, busqueda, filtro]);

  useEffect(() => { cargar(); }, [cargar]);

  const descargar = async (contrato) => {
    try {
      setDescargando(contrato.id);
      const url = getMinutaUrl(contrato.id);
      const nombre = `MINUTA_${contrato.numero}_${contrato.estado}.docx`;
      const { uri } = await FileSystem.downloadAsync(url, FileSystem.documentDirectory + nombre);
      await Sharing.shareAsync(uri, {
        mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
    } catch {
      Alert.alert('Error', 'No se pudo generar la minuta');
    } finally {
      setDescargando(null);
    }
  };

  // ── Modal selector de proyecto ──────────────────────────────────────────────
  const ModalProyecto = () => (
    <Modal visible={modalVisible} transparent animationType="fade">
      <View style={styles.modalOverlay}>
        <View style={styles.modalBox}>
          <Text style={styles.modalTitulo}>Seleccionar Proyecto</Text>
          {proyectos.map((p, i) => (
            <TouchableOpacity
              key={p.id}
              style={styles.proyectoBtn}
              onPress={() => { setProyecto(p); setModalVisible(false); }}
            >
              <Text style={styles.proyectoIcono}>{ICONOS_PROYECTO[i] || '📁'}</Text>
              <View style={styles.proyectoInfo}>
                <Text style={styles.proyectoNombre}>{p.nombre}</Text>
                <Text style={styles.proyectoMoneda}>{p.moneda}</Text>
              </View>
              <Text style={styles.proyectoArrow}>›</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </Modal>
  );

  // ── Header con proyecto activo ───────────────────────────────────────────────
  const Header = () => (
    <TouchableOpacity style={styles.headerProyecto} onPress={() => setModalVisible(true)}>
      <Text style={styles.headerProyectoTxt} numberOfLines={1}>
        {proyecto ? `${ICONOS_PROYECTO[proyectos.findIndex(p => p.id === proyecto.id)] || '📁'} ${proyecto.nombre}` : 'Seleccionar proyecto...'}
      </Text>
      <Text style={styles.headerCambiar}>cambiar ›</Text>
    </TouchableOpacity>
  );

  // ── Tarjeta de contrato ───────────────────────────────────────────────────────
  const renderContrato = ({ item }) => {
    const color = COLORES[item.estado] || COLORES.VERDE;
    const bajando = descargando === item.id;
    const monedaSimbolo = item.moneda === 'DOLARES' ? 'US$' : 'S/';

    return (
      <View style={[styles.card, { borderLeftColor: color.border }]}>
        <View style={styles.cardHeader}>
          <View style={[styles.badge, { backgroundColor: color.bg }]}>
            <Text style={[styles.badgeText, { color: color.text }]}>{item.estado}</Text>
          </View>
          <Text style={styles.cardNumero}>N° {item.numero}</Text>
        </View>

        <Text style={styles.cardTitular}>{item.titular}</Text>

        {item.lote && (
          <Text style={styles.cardSub}>MZ {item.lote.manzana} · Lote {item.lote.numero} · {item.lote.area} m²</Text>
        )}

        <View style={styles.cardMontos}>
          <View style={styles.montoItem}>
            <Text style={styles.montoLabel}>Precio</Text>
            <Text style={styles.montoValor}>{monedaSimbolo} {item.precio?.toLocaleString('es-PE')}</Text>
          </View>
          <View style={styles.montoItem}>
            <Text style={styles.montoLabel}>Pagado</Text>
            <Text style={styles.montoValor}>{monedaSimbolo} {item.pago?.toLocaleString('es-PE')}</Text>
          </View>
          <View style={styles.montoItem}>
            <Text style={[styles.montoLabel, item.saldo > 0 && { color: '#dc2626' }]}>Saldo</Text>
            <Text style={[styles.montoValor, item.saldo > 0 && { color: '#dc2626' }]}>
              {monedaSimbolo} {item.saldo?.toLocaleString('es-PE')}
            </Text>
          </View>
        </View>

        <TouchableOpacity
          style={[styles.btnMinuta, bajando && styles.btnMinutaOff]}
          onPress={() => descargar(item)}
          disabled={bajando}
        >
          {bajando
            ? <ActivityIndicator color="#fff" size="small" />
            : <Text style={styles.btnMinutaTxt}>📄 Generar Minuta</Text>
          }
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <ModalProyecto />
      <Header />

      {proyecto && (
        <>
          <View style={styles.searchWrap}>
            <TextInput
              style={styles.searchInput}
              placeholder="Buscar titular..."
              value={busqueda}
              onChangeText={setBusqueda}
              onSubmitEditing={cargar}
              returnKeyType="search"
            />
          </View>

          <View style={styles.filtros}>
            {FILTROS.map(f => (
              <TouchableOpacity
                key={f}
                style={[styles.filtroBtn, filtro === f && styles.filtroBtnOn]}
                onPress={() => setFiltro(f)}
              >
                <Text style={[styles.filtroTxt, filtro === f && styles.filtroTxtOn]}>{f}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {loading
            ? <View style={styles.center}><ActivityIndicator size="large" color="#1a56db" /></View>
            : <FlatList
                data={contratos}
                keyExtractor={i => i.id.toString()}
                renderItem={renderContrato}
                contentContainerStyle={styles.lista}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); cargar(); }} />}
                ListEmptyComponent={<Text style={styles.empty}>No hay contratos</Text>}
              />
          }
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container:        { flex: 1, backgroundColor: '#f3f4f6' },
  center:           { flex: 1, justifyContent: 'center', alignItems: 'center' },
  // Modal
  modalOverlay:     { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', padding: 24 },
  modalBox:         { backgroundColor: '#fff', borderRadius: 16, padding: 20 },
  modalTitulo:      { fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 16, textAlign: 'center' },
  proyectoBtn:      { flexDirection: 'row', alignItems: 'center', padding: 14, borderRadius: 10, backgroundColor: '#f9fafb', marginBottom: 10 },
  proyectoIcono:    { fontSize: 28, marginRight: 12 },
  proyectoInfo:     { flex: 1 },
  proyectoNombre:   { fontSize: 15, fontWeight: '600', color: '#111827' },
  proyectoMoneda:   { fontSize: 12, color: '#6b7280', marginTop: 2 },
  proyectoArrow:    { fontSize: 20, color: '#9ca3af' },
  // Header proyecto
  headerProyecto:   { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#1e40af', padding: 12, paddingHorizontal: 16 },
  headerProyectoTxt:{ flex: 1, color: '#fff', fontWeight: '600', fontSize: 14 },
  headerCambiar:    { color: '#93c5fd', fontSize: 13, marginLeft: 8 },
  // Búsqueda y filtros
  searchWrap:       { padding: 12, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
  searchInput:      { backgroundColor: '#f3f4f6', borderRadius: 8, padding: 10, fontSize: 15 },
  filtros:          { flexDirection: 'row', padding: 8, backgroundColor: '#fff', gap: 6 },
  filtroBtn:        { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 20, backgroundColor: '#f3f4f6' },
  filtroBtnOn:      { backgroundColor: '#1a56db' },
  filtroTxt:        { fontSize: 12, color: '#6b7280', fontWeight: '500' },
  filtroTxtOn:      { color: '#fff' },
  // Lista
  lista:            { padding: 12, gap: 12 },
  empty:            { textAlign: 'center', color: '#9ca3af', marginTop: 40 },
  // Card
  card:             { backgroundColor: '#fff', borderRadius: 12, padding: 14, borderLeftWidth: 4, elevation: 2, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4 },
  cardHeader:       { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  badge:            { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20 },
  badgeText:        { fontSize: 11, fontWeight: '700' },
  cardNumero:       { fontSize: 13, color: '#6b7280' },
  cardTitular:      { fontSize: 15, fontWeight: '600', color: '#111827', marginBottom: 3 },
  cardSub:          { fontSize: 13, color: '#6b7280', marginBottom: 8 },
  cardMontos:       { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#f9fafb', borderRadius: 8, padding: 10, marginBottom: 12 },
  montoItem:        { alignItems: 'center' },
  montoLabel:       { fontSize: 11, color: '#6b7280', marginBottom: 2 },
  montoValor:       { fontSize: 13, fontWeight: '600', color: '#111827' },
  btnMinuta:        { backgroundColor: '#1a56db', borderRadius: 8, padding: 10, alignItems: 'center' },
  btnMinutaOff:     { backgroundColor: '#93c5fd' },
  btnMinutaTxt:     { color: '#fff', fontWeight: '600', fontSize: 14 },
});
