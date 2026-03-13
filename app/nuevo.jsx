import { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, ActivityIndicator, Alert, Switch
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { getManzanas, getLotes, getRegiones, getProvincias, getDistritos, crearContrato } from '../src/api';
import { useProyecto } from './_layout';

const GENEROS       = [{ label: 'Masculino', value: 'M' }, { label: 'Femenino', value: 'F' }];
const ESTADOS_CIVIL = [
  { label: 'Soltero(a)',    value: 'S' },
  { label: 'Casado(a)',     value: 'C' },
  { label: 'Divorciado(a)', value: 'D' },
  { label: 'Viudo(a)',      value: 'V' },
];

const Campo = ({ label, value, onChange, ...props }) => (
  <View style={styles.campo}>
    <Text style={styles.label}>{label}</Text>
    <TextInput style={styles.input} value={value} onChangeText={onChange}
      placeholderTextColor="#9ca3af" {...props} />
  </View>
);

const Selector = ({ label, value, onChange, items }) => (
  <View style={styles.campo}>
    <Text style={styles.label}>{label}</Text>
    <View style={styles.pickerWrap}>
      <Picker selectedValue={value} onValueChange={onChange} style={styles.picker}>
        <Picker.Item label="— Seleccionar —" value="" />
        {items.map(i => (
          <Picker.Item key={i.value ?? i} label={i.label ?? i} value={i.value ?? i} />
        ))}
      </Picker>
    </View>
  </View>
);

const Seccion = ({ titulo }) => (
  <View style={styles.seccion}>
    <Text style={styles.seccionTxt}>{titulo}</Text>
  </View>
);

export default function NuevoContrato() {
  const { proyecto } = useProyecto();
  const esDolares = proyecto?.moneda === 'DOLARES';

  const [guardando, setGuardando] = useState(false);

  // Lote
  const [manzanas, setManzanas] = useState([]);
  const [manzana,  setManzana]  = useState('');
  const [lotes,    setLotes]    = useState([]);
  const [loteId,   setLoteId]   = useState('');

  // Económico
  const [precio,      setPrecio]      = useState('');
  const [pago,        setPago]        = useState('');
  const [tieneSep,    setTieneSep]    = useState(false);
  const [sep,         setSep]         = useState('');        // en moneda del proyecto
  const [sepSoles,    setSepSoles]    = useState('');        // solo si dólares
  const [tipoCambio,  setTipoCambio]  = useState('');

  // Plazo: fecha fija o meses
  const [usaMeses,    setUsaMeses]    = useState(esDolares);
  const [fechaPago,   setFechaPago]   = useState('');
  const [plazoMeses,  setPlazoMeses]  = useState('');

  // Titular
  const [titular,     setTitular]     = useState('');
  const [dni,         setDni]         = useState('');
  const [ocupacion,   setOcupacion]   = useState('');
  const [genero,      setGenero]      = useState('');
  const [estadoCivil, setEstadoCivil] = useState('');
  const [direccion,   setDireccion]   = useState('');
  const [region1,     setRegion1]     = useState('');
  const [prov1,       setProv1]       = useState('');
  const [dist1Id,     setDist1Id]     = useState('');
  const [regiones,    setRegiones]    = useState([]);
  const [provs1,      setProvs1]      = useState([]);
  const [dists1,      setDists1]      = useState([]);

  // Copropietario
  const [tieneCoprop,   setTieneCoprop]   = useState(false);
  const [coprop,        setCoprop]        = useState('');
  const [dni2,          setDni2]          = useState('');
  const [ocupacion2,    setOcupacion2]    = useState('');
  const [genero2,       setGenero2]       = useState('');
  const [estadoCivil2,  setEstadoCivil2]  = useState('');
  const [direccion2,    setDireccion2]    = useState('');
  const [region2,       setRegion2]       = useState('');
  const [prov2,         setProv2]         = useState('');
  const [dist2Id,       setDist2Id]       = useState('');
  const [provs2,        setProvs2]        = useState([]);
  const [dists2,        setDists2]        = useState([]);

  useEffect(() => {
    if (proyecto) {
      getManzanas(proyecto.id).then(setManzanas).catch(() => {});
      getRegiones().then(setRegiones).catch(() => {});
      setUsaMeses(esDolares);
    }
  }, [proyecto]);

  useEffect(() => {
    if (manzana && proyecto) {
      getLotes(proyecto.id, manzana).then(setLotes).catch(() => {});
      setLoteId('');
    }
  }, [manzana]);

  // Cascada titular
  useEffect(() => {
    if (region1) { getProvincias(region1).then(setProvs1).catch(() => {}); setProv1(''); setDists1([]); setDist1Id(''); }
  }, [region1]);
  useEffect(() => {
    if (region1 && prov1) { getDistritos(region1, prov1).then(setDists1).catch(() => {}); setDist1Id(''); }
  }, [prov1]);

  // Cascada coprop
  useEffect(() => {
    if (region2) { getProvincias(region2).then(setProvs2).catch(() => {}); setProv2(''); setDists2([]); setDist2Id(''); }
  }, [region2]);
  useEffect(() => {
    if (region2 && prov2) { getDistritos(region2, prov2).then(setDists2).catch(() => {}); setDist2Id(''); }
  }, [prov2]);

  const guardar = async () => {
    if (!proyecto) { Alert.alert('Selecciona un proyecto primero'); return; }
    if (!titular || !loteId || !precio) { Alert.alert('Faltan datos', 'Completa titular, lote y precio'); return; }

    const numero = Date.now() % 100000;

    const data = {
      numero,
      proyecto_id:   proyecto.id,
      lote_id:       parseInt(loteId),
      fecha:         new Date().toISOString().slice(0, 10),
      titular:       titular.toUpperCase(),
      dni:           dni || null,
      ocupacion1:    ocupacion || null,
      genero1:       genero || null,
      estado_civil1: estadoCivil || null,
      distrito1_id:  dist1Id ? parseInt(dist1Id) : null,
      direccion1:    direccion || null,
      copropietario: tieneCoprop ? coprop.toUpperCase() : null,
      dni2:          tieneCoprop ? (dni2 || null) : null,
      ocupacion2:    tieneCoprop ? (ocupacion2 || null) : null,
      genero2:       tieneCoprop ? (genero2 || null) : null,
      estado_civil2: tieneCoprop ? (estadoCivil2 || null) : null,
      distrito2_id:  tieneCoprop && dist2Id ? parseInt(dist2Id) : null,
      direccion2:    tieneCoprop ? (direccion2 || null) : null,
      moneda:        proyecto.moneda,
      precio:        parseFloat(precio),
      separacion:    tieneSep ? (parseFloat(sep) || 0) : 0,
      sep_en_soles:  tieneSep && esDolares ? (parseFloat(sepSoles) || null) : null,
      tipo_cambio:   tieneSep && esDolares ? (parseFloat(tipoCambio) || null) : null,
      pago:          parseFloat(pago) || 0,
      f_pago_total:  !usaMeses && fechaPago ? fechaPago : null,
      plazo_meses:   usaMeses && plazoMeses ? parseInt(plazoMeses) : null,
    };

    try {
      setGuardando(true);
      await crearContrato(data);
      Alert.alert('✅ Guardado', 'Contrato registrado', [{ text: 'OK', onPress: limpiar }]);
    } catch (e) {
      Alert.alert('Error', e.response?.data?.detail || 'Error al guardar');
    } finally {
      setGuardando(false);
    }
  };

  const limpiar = () => {
    setTitular(''); setDni(''); setOcupacion(''); setGenero(''); setEstadoCivil('');
    setDireccion(''); setRegion1(''); setProv1(''); setDist1Id('');
    setPrecio(''); setPago(''); setSep(''); setSepSoles(''); setTipoCambio('');
    setFechaPago(''); setPlazoMeses(''); setManzana(''); setLoteId('');
    setTieneCoprop(false); setCoprop(''); setDni2(''); setOcupacion2('');
    setGenero2(''); setEstadoCivil2(''); setDireccion2(''); setRegion2('');
  };

  if (!proyecto) {
    return (
      <View style={styles.center}>
        <Text style={styles.sinProyecto}>Selecciona un proyecto en la pestaña "Contratos"</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>

      <Seccion titulo="📍 Lote" />
      <Selector label="Manzana" value={manzana} onChange={setManzana} items={manzanas} />
      {manzana && (
        <Selector label="Lote" value={loteId} onChange={setLoteId}
          items={lotes.map(l => ({ label: `Lote ${l.numero} — ${l.area} m²`, value: l.id.toString() }))} />
      )}

      <Seccion titulo="💰 Datos Económicos" />
      <Campo label={`Precio (${esDolares ? 'US$' : 'S/'})`} value={precio} onChange={setPrecio}
        keyboardType="decimal-pad" placeholder="0.00" />

      <View style={styles.switchRow}>
        <Text style={styles.switchLabel}>¿Tiene separación?</Text>
        <Switch value={tieneSep} onValueChange={setTieneSep} trackColor={{ true: '#1a56db' }} />
      </View>

      {tieneSep && (
        <>
          {esDolares && (
            <>
              <Campo label="Separación en soles (S/)" value={sepSoles} onChange={setSepSoles}
                keyboardType="decimal-pad" placeholder="0.00" />
              <Campo label="Tipo de cambio" value={tipoCambio} onChange={setTipoCambio}
                keyboardType="decimal-pad" placeholder="4.00" />
              <Campo label="Equivalente en dólares (US$)" value={sep} onChange={setSep}
                keyboardType="decimal-pad" placeholder="0.00" />
            </>
          )}
          {!esDolares && (
            <Campo label="Separación (S/)" value={sep} onChange={setSep}
              keyboardType="decimal-pad" placeholder="0.00" />
          )}
        </>
      )}

      <Campo label={`Pago realizado (${esDolares ? 'US$' : 'S/'})`} value={pago} onChange={setPago}
        keyboardType="decimal-pad" placeholder="0.00" />

      <View style={styles.switchRow}>
        <Text style={styles.switchLabel}>Plazo en meses (no fecha fija)</Text>
        <Switch value={usaMeses} onValueChange={setUsaMeses} trackColor={{ true: '#1a56db' }} />
      </View>

      {usaMeses
        ? <Campo label="Plazo (meses)" value={plazoMeses} onChange={setPlazoMeses}
            keyboardType="numeric" placeholder="18" />
        : <Campo label="Fecha límite de pago (YYYY-MM-DD)" value={fechaPago} onChange={setFechaPago}
            placeholder="2026-01-15" />
      }

      <Seccion titulo="👤 Titular" />
      <Campo label="Nombre completo" value={titular} onChange={setTitular}
        autoCapitalize="characters" placeholder="JUAN PÉREZ GÓMEZ" />
      <Campo label="DNI" value={dni} onChange={setDni} keyboardType="numeric" maxLength={8} />
      <Campo label="Ocupación" value={ocupacion} onChange={setOcupacion} placeholder="COMERCIANTE" />
      <Selector label="Género" value={genero} onChange={setGenero} items={GENEROS} />
      <Selector label="Estado civil" value={estadoCivil} onChange={setEstadoCivil} items={ESTADOS_CIVIL} />
      <Campo label="Dirección" value={direccion} onChange={setDireccion} multiline />

      <Seccion titulo="📌 Ubigeo del Titular" />
      <Selector label="Región" value={region1} onChange={setRegion1} items={regiones} />
      {region1 && <Selector label="Provincia" value={prov1} onChange={setProv1} items={provs1} />}
      {prov1 && (
        <Selector label="Distrito" value={dist1Id} onChange={setDist1Id}
          items={dists1.map(d => ({ label: d.distrito, value: d.id.toString() }))} />
      )}

      <Seccion titulo="👥 Copropietario" />
      <View style={styles.switchRow}>
        <Text style={styles.switchLabel}>¿Tiene copropietario?</Text>
        <Switch value={tieneCoprop} onValueChange={setTieneCoprop} trackColor={{ true: '#1a56db' }} />
      </View>

      {tieneCoprop && (
        <>
          <Campo label="Nombre completo" value={coprop} onChange={setCoprop} autoCapitalize="characters" />
          <Campo label="DNI" value={dni2} onChange={setDni2} keyboardType="numeric" maxLength={8} />
          <Campo label="Ocupación" value={ocupacion2} onChange={setOcupacion2} />
          <Selector label="Género" value={genero2} onChange={setGenero2} items={GENEROS} />
          <Selector label="Estado civil" value={estadoCivil2} onChange={setEstadoCivil2} items={ESTADOS_CIVIL} />
          <Campo label="Dirección" value={direccion2} onChange={setDireccion2} multiline />
          <Seccion titulo="📌 Ubigeo del Copropietario" />
          <Selector label="Región" value={region2} onChange={setRegion2} items={regiones} />
          {region2 && <Selector label="Provincia" value={prov2} onChange={setProv2} items={provs2} />}
          {prov2 && (
            <Selector label="Distrito" value={dist2Id} onChange={setDist2Id}
              items={dists2.map(d => ({ label: d.distrito, value: d.id.toString() }))} />
          )}
        </>
      )}

      <TouchableOpacity
        style={[styles.btnGuardar, guardando && styles.btnGuardarOff]}
        onPress={guardar} disabled={guardando}
      >
        {guardando
          ? <ActivityIndicator color="#fff" />
          : <Text style={styles.btnGuardarTxt}>✓ Registrar Contrato</Text>
        }
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:       { flex: 1, backgroundColor: '#f3f4f6' },
  content:         { padding: 16 },
  center:          { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  sinProyecto:     { textAlign: 'center', color: '#6b7280', fontSize: 15 },
  seccion:         { backgroundColor: '#1a56db', borderRadius: 8, padding: 10, marginTop: 16, marginBottom: 8 },
  seccionTxt:      { color: '#fff', fontWeight: '700', fontSize: 14 },
  campo:           { marginBottom: 12 },
  label:           { fontSize: 13, color: '#374151', fontWeight: '500', marginBottom: 4 },
  input:           { backgroundColor: '#fff', borderRadius: 8, padding: 12, fontSize: 15, borderWidth: 1, borderColor: '#e5e7eb' },
  pickerWrap:      { backgroundColor: '#fff', borderRadius: 8, borderWidth: 1, borderColor: '#e5e7eb', overflow: 'hidden' },
  picker:          { height: 50 },
  switchRow:       { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#fff', borderRadius: 8, padding: 12, marginBottom: 12, borderWidth: 1, borderColor: '#e5e7eb' },
  switchLabel:     { fontSize: 14, color: '#374151', flex: 1 },
  btnGuardar:      { backgroundColor: '#16a34a', borderRadius: 10, padding: 16, alignItems: 'center', marginTop: 20 },
  btnGuardarOff:   { backgroundColor: '#86efac' },
  btnGuardarTxt:   { color: '#fff', fontWeight: '700', fontSize: 16 },
});
