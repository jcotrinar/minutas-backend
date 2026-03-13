import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { createContext, useContext, useState } from 'react';

// Contexto global del proyecto seleccionado
export const ProyectoContext = createContext(null);

export function useProyecto() {
  return useContext(ProyectoContext);
}

export default function Layout() {
  const [proyecto, setProyecto] = useState(null);

  return (
    <ProyectoContext.Provider value={{ proyecto, setProyecto }}>
      <Tabs
        screenOptions={{
          tabBarActiveTintColor: '#1a56db',
          tabBarInactiveTintColor: '#6b7280',
          tabBarStyle: { backgroundColor: '#fff', borderTopColor: '#e5e7eb' },
          headerStyle: { backgroundColor: '#1a56db' },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: 'bold' },
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            title: proyecto ? proyecto.nombre : 'Minutas',
            tabBarLabel: 'Contratos',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="document-text-outline" color={color} size={size} />
            ),
          }}
        />
        <Tabs.Screen
          name="nuevo"
          options={{
            title: 'Nuevo Contrato',
            tabBarLabel: 'Nuevo',
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="add-circle-outline" color={color} size={size} />
            ),
          }}
        />
      </Tabs>
    </ProyectoContext.Provider>
  );
}
