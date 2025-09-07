import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../src/App'

// Mock the store
vi.mock('../src/store/useAppStore', () => ({
  default: () => ({
    theme: 'light',
    currentPage: 'upload'
  })
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('Infotainment Accessibility Evaluator')).toBeInTheDocument()
  })

  it('renders upload page by default', () => {
    render(<App />)
    expect(screen.getByText('Upload your infotainment UI code')).toBeInTheDocument()
  })
})
