import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import RoomsPage from './pages/RoomsPage'
import ProtectedRoute from './components/ProtectedRoute'

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
                    <RoomsPage />
                </ProtectedRoute>
            }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
