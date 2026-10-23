function handleUnauthorized(response, navigate) {
  if (response.status === 401) {
    localStorage.removeItem('access_token')
    navigate('/login')
    return true
  }

  return false
}

export default handleUnauthorized