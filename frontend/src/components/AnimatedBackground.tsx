import { useEffect, useState } from 'react'

export function AnimatedBackground() {
	const [shapes, setShapes] = useState<Array<{
		id: number
		size: number
		initialX: number
		initialY: number
		rotation: number
		animationDelay: number
	}>>([])

	useEffect(() => {
		// Generate random shapes for the background
		const newShapes = Array.from({ length: 6 }, (_, i) => ({
			id: i,
			size: Math.random() * 200 + 100,
			initialX: Math.random() * 100,
			initialY: Math.random() * 100,
			rotation: Math.random() * 360,
			animationDelay: Math.random() * 10,
		}))
		setShapes(newShapes)
	}, [])

	return (
		<div className="fixed inset-0 overflow-hidden pointer-events-none">
			{/* Gradient Overlay */}
			<div className="absolute inset-0 bg-gradient-depth opacity-60" />

			{/* Animated Shapes */}
			{shapes.map((shape) => (
				<div
					key={shape.id}
					className="absolute opacity-20 dark:opacity-30"
					style={{
						width: `${shape.size}px`,
						height: `${shape.size}px`,
						left: `${shape.initialX}%`,
						top: `${shape.initialY}%`,
						transform: `rotate(${shape.rotation}deg)`,
						animationDelay: `${shape.animationDelay}s`,
					}}
				>
					{/* Crystalline faceted shapes */}
					<div className="w-full h-full bg-gradient-to-br from-primary/30 to-secondary/20 animate-float"
						style={{
							clipPath: 'polygon(50% 0%, 85% 15%, 100% 45%, 85% 85%, 50% 100%, 15% 85%, 0% 45%, 15% 15%)',
						}} />
				</div>
			))}

			{/* Crystalline floating elements */}
			<div className="absolute top-1/4 left-1/4 w-32 h-32 bg-primary/10 animate-slide-diagonal"
				style={{ clipPath: 'polygon(50% 0%, 90% 20%, 80% 60%, 100% 80%, 60% 100%, 20% 90%, 0% 50%, 30% 10%)' }} />

			<div className="absolute top-1/2 right-1/3 w-24 h-24 bg-secondary/15 animate-float"
				style={{ clipPath: 'polygon(50% 0%, 100% 30%, 85% 70%, 100% 100%, 50% 85%, 0% 100%, 15% 70%, 0% 30%)' }} />

			<div className="absolute bottom-1/3 left-1/2 w-20 h-20 bg-accent/20 animate-slide-diagonal"
				style={{
					clipPath: 'polygon(50% 0%, 80% 10%, 100% 40%, 90% 70%, 70% 100%, 30% 100%, 10% 70%, 0% 40%, 20% 10%)',
					animationDelay: '5s'
				}} />
		</div>
	)
}