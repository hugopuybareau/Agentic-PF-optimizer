import { Navigation } from '@/components/Navigation'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

const portfolioData = [
  { name: 'Apple Inc.', symbol: 'AAPL', value: 45000, allocation: 32, risk: 'Medium', type: 'Stock' },
  { name: 'Microsoft Corp.', symbol: 'MSFT', value: 38000, allocation: 27, risk: 'Low', type: 'Stock' },
  { name: 'Tesla Inc.', symbol: 'TSLA', value: 22000, allocation: 16, risk: 'High', type: 'Stock' },
  { name: 'S&P 500 ETF', symbol: 'SPY', value: 18000, allocation: 13, risk: 'Low', type: 'ETF' },
  { name: 'Bitcoin', symbol: 'BTC', value: 12000, allocation: 9, risk: 'High', type: 'Crypto' },
  { name: 'Cash', symbol: 'USD', value: 5000, allocation: 3, risk: 'None', type: 'Cash' },
]

const allocationData = [
  { name: 'Stocks', value: 105000, color: 'hsl(var(--primary))' },
  { name: 'ETFs', value: 18000, color: 'hsl(var(--secondary))' },
  { name: 'Crypto', value: 12000, color: 'hsl(var(--accent))' },
  { name: 'Cash', value: 5000, color: 'hsl(var(--muted-foreground))' },
]

const chartColors = [
  'hsl(var(--primary))',
  'hsl(var(--secondary))', 
  'hsl(var(--accent))',
  'hsl(var(--muted-foreground))',
  'hsl(var(--primary) / 0.7)',
  'hsl(var(--secondary) / 0.7)',
]

const performanceData = [
  { month: 'Jan', value: 125000 },
  { month: 'Feb', value: 132000 },
  { month: 'Mar', value: 128000 },
  { month: 'Apr', value: 135000 },
  { month: 'May', value: 140000 },
  { month: 'Jun', value: 140000 },
]

export default function Portfolio() {
  const totalValue = portfolioData.reduce((sum, item) => sum + item.value, 0)

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'High': return 'bg-destructive/20 text-destructive'
      case 'Medium': return 'bg-accent/20 text-accent-foreground'
      case 'Low': return 'bg-secondary/20 text-secondary-foreground'
      default: return 'bg-muted/20 text-muted-foreground'
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-20 px-6 pb-12">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-hero mb-2">Portfolio Overview</h1>
            <p className="text-sub">Track your investments and performance</p>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="card-platine p-6 rounded-lg">
              <h3 className="text-sub mb-2">Total Value</h3>
              <p className="text-2xl font-semibold">
                ${totalValue.toLocaleString()}
              </p>
              <p className="text-xs text-green-600 mt-1">+2.3% this month</p>
            </div>
            
            <div className="card-platine p-6 rounded-lg">
              <h3 className="text-sub mb-2">Risk Level</h3>
              <p className="text-2xl font-semibold">Medium</p>
              <p className="text-xs text-muted-foreground mt-1">Balanced allocation</p>
            </div>
            
            <div className="card-platine p-6 rounded-lg">
              <h3 className="text-sub mb-2">Diversification</h3>
              <p className="text-2xl font-semibold">85%</p>
              <p className="text-xs text-blue-600 mt-1">Well diversified</p>
            </div>
            
            <div className="card-platine p-6 rounded-lg">
              <h3 className="text-sub mb-2">Monthly Return</h3>
              <p className="text-2xl font-semibold">+3.2%</p>
              <p className="text-xs text-green-600 mt-1">Outperforming S&P</p>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Portfolio Holdings */}
            <div className="lg:col-span-2">
              <div className="card-platine p-6 rounded-lg">
                <h2 className="text-nav font-medium mb-6">Holdings</h2>
                <div className="space-y-4">
                  {portfolioData.map((asset) => (
                    <div key={asset.symbol} className="flex items-center justify-between p-4 rounded-lg hover:bg-accent/10 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                          <span className="text-xs font-medium">{asset.symbol.substring(0, 2)}</span>
                        </div>
                        <div>
                          <h3 className="text-nav font-medium">{asset.name}</h3>
                          <p className="text-sub">{asset.symbol} • {asset.type}</p>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <p className="text-nav font-medium">${asset.value.toLocaleString()}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-sub">{asset.allocation}%</span>
                          <span className={`px-2 py-1 rounded text-xs ${getRiskBadgeColor(asset.risk)}`}>
                            {asset.risk}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="space-y-6">
              {/* Allocation Chart */}
              <div className="card-platine p-6 rounded-lg">
                <h2 className="text-nav font-medium mb-4">Allocation</h2>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={allocationData}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {allocationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                       <Tooltip 
                        formatter={(value: number) => [`$${value.toLocaleString()}`, 'Value']}
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          color: 'hsl(var(--card-foreground))',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Legend */}
                <div className="space-y-2 mt-4">
                  {allocationData.map((item) => (
                    <div key={item.name} className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sub">{item.name}</span>
                      </div>
                      <span className="text-nav">${item.value.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Performance Chart */}
              <div className="card-platine p-6 rounded-lg">
                <h2 className="text-nav font-medium mb-4">6M Performance</h2>
                <div className="h-32">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={performanceData}>
                      <XAxis 
                        dataKey="month" 
                        axisLine={false} 
                        tickLine={false}
                        tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <YAxis hide />
                       <Tooltip 
                        formatter={(value: number) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          color: 'hsl(var(--card-foreground))',
                        }}
                      />
                      <Bar 
                        dataKey="value" 
                        fill="hsl(var(--primary))" 
                        radius={[2, 2, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}