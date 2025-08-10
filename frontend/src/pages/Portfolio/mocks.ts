export const portfolioData = [
    { name: 'Apple Inc.', symbol: 'AAPL', value: 45000, allocation: 32, risk: 'Medium', type: 'Stock' },
    { name: 'Microsoft Corp.', symbol: 'MSFT', value: 38000, allocation: 27, risk: 'Low', type: 'Stock' },
    { name: 'Tesla Inc.', symbol: 'TSLA', value: 22000, allocation: 16, risk: 'High', type: 'Stock' },
    { name: 'S&P 500 ETF', symbol: 'SPY', value: 18000, allocation: 13, risk: 'Low', type: 'ETF' },
    { name: 'Bitcoin', symbol: 'BTC', value: 12000, allocation: 9, risk: 'High', type: 'Crypto' },
    { name: 'Cash', symbol: 'USD', value: 5000, allocation: 3, risk: 'None', type: 'Cash' },
  ]
  
  export const allocationData = [
    { name: 'Stocks', value: 105000, color: 'hsl(var(--primary))' },
    { name: 'ETFs', value: 18000, color: 'hsl(var(--secondary))' },
    { name: 'Crypto', value: 12000, color: 'hsl(var(--accent))' },
    { name: 'Cash', value: 5000, color: 'hsl(var(--muted-foreground))' },
  ]
  
// TODO: check if we need this

//   export const chartColors = [
//     'hsl(var(--primary))',
//     'hsl(var(--secondary))', 
//     'hsl(var(--accent))',
//     'hsl(var(--muted-foreground))',
//     'hsl(var(--primary) / 0.7)',
//     'hsl(var(--secondary) / 0.7)',
//   ]
  
  export const performanceData = [
    { month: 'Jan', value: 125000 },
    { month: 'Feb', value: 132000 },
    { month: 'Mar', value: 128000 },
    { month: 'Apr', value: 135000 },
    { month: 'May', value: 140000 },
    { month: 'Jun', value: 140000 },
  ]