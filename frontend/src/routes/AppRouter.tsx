import { Navigate, createBrowserRouter } from "react-router-dom";

import { AuthLayout, DashboardLayout } from "@/layouts";
import {
  CamerasPage,
  DashboardPage,
  EventsPage,
  LoginPage,
  NotFoundPage,
  SettingsPage,
  StatisticsPage,
} from "@/pages";

export const appRouter = createBrowserRouter([
  {
    path: "/login",
    element: <AuthLayout />,
    children: [{ index: true, element: <LoginPage /> }],
  },
  {
    path: "/",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "cameras", element: <CamerasPage /> },
      { path: "events", element: <EventsPage /> },
      { path: "statistics", element: <StatisticsPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);
