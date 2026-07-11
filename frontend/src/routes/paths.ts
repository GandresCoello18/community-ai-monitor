export const paths = {
  home: "/",
  login: "/login",
  dashboard: "/dashboard",
  cameras: "/cameras",
  events: "/events",
  statistics: "/statistics",
  settings: "/settings",
} as const;

export type AppPath = (typeof paths)[keyof typeof paths];

export interface NavItem {
  label: string;
  path: AppPath;
}

export const mainNavItems: NavItem[] = [
  { label: "Panel", path: paths.dashboard },
  { label: "Cámaras", path: paths.cameras },
  { label: "Eventos", path: paths.events },
  { label: "Estadísticas", path: paths.statistics },
  { label: "Configuración", path: paths.settings },
];
