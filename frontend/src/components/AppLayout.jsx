import Navbar from './Navbar'

function AppLayout({ children }) {
  return (
    <>
      <Navbar />

      <main className="app-main">
        {children}
      </main>
    </>
  )
}

export default AppLayout
