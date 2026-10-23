import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import RoomsPage from './pages/RoomsPage'
import ProtectedRoute from './components/ProtectedRoute'
import ReservationPage from './pages/ReservationPage'
import ReservationsPage from './pages/ReservationsPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import AppLayout from './components/AppLayout'
import GoogleCalendarPage from './pages/GoogleCalendarPage'
import AISearchPage from './pages/AiSearchPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/rooms"
          element={
            <ProtectedRoute>
              <AppLayout>
                <RoomsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/reservations"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ReservationsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/rooms/:roomId/reserve"
          element={
            <ProtectedRoute>
              <AppLayout>
                <ReservationPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route
          path="/google-calendar"
          element={
            <ProtectedRoute>
              <AppLayout>
                <GoogleCalendarPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-search"
          element={
            <ProtectedRoute>
              <AppLayout>
                <AISearchPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
