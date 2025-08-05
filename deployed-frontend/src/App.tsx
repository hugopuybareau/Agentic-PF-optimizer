import Landing from '@/components/Landing'
import { ThemeProvider } from '@/hooks/use-theme'

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="silver-ui-theme">
      <Landing />
    </ThemeProvider>
  )
}

export default App