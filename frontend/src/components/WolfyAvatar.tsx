import React from 'react';
import { motion } from 'framer-motion';

interface WolfyAvatarProps {
  size?: 'sm' | 'md' | 'lg';
  isActive?: boolean;
  className?: string;
}

export function WolfyAvatar({ size = 'md', isActive = false, className = '' }: WolfyAvatarProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <motion.div
      className={`${sizeClasses[size]} ${className} relative`}
      animate={isActive ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
    >
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Wolf head background */}
        <motion.circle
          cx="50"
          cy="50"
          r="35"
          fill="#14B8A6"
          className="drop-shadow-lg"
        />
        
        {/* Wolf face */}
        <motion.ellipse
          cx="50"
          cy="45"
          rx="25"
          ry="20"
          fill="#0F172A"
        />
        
        {/* Ears */}
        <motion.path
          d="M35 30 L40 15 L45 30 Z"
          fill="#14B8A6"
          animate={isActive ? { rotate: [-2, 2, -2] } : {}}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          style={{ transformOrigin: '40px 25px' }}
        />
        <motion.path
          d="M55 30 L60 15 L65 30 Z"
          fill="#14B8A6"
          animate={isActive ? { rotate: [2, -2, 2] } : {}}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut', delay: 0.2 }}
          style={{ transformOrigin: '60px 25px' }}
        />
        
        {/* Inner ears */}
        <path d="M37 28 L40 20 L43 28 Z" fill="#0D9488" />
        <path d="M57 28 L60 20 L63 28 Z" fill="#0D9488" />
        
        {/* Eyes */}
        <motion.circle
          cx="42"
          cy="42"
          r="3"
          fill="#FFFFFF"
          animate={isActive ? { scaleY: [1, 0.1, 1] } : {}}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.circle
          cx="58"
          cy="42"
          r="3"
          fill="#FFFFFF"
          animate={isActive ? { scaleY: [1, 0.1, 1] } : {}}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
        
        {/* Eye pupils */}
        <circle cx="42" cy="42" r="1.5" fill="#0F172A" />
        <circle cx="58" cy="42" r="1.5" fill="#0F172A" />
        
        {/* Nose */}
        <path d="M48 48 L50 52 L52 48 Z" fill="#0F172A" />
        
        {/* Mouth */}
        <motion.path
          d="M46 55 Q50 58 54 55"
          stroke="#0F172A"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
          animate={isActive ? { d: ["M46 55 Q50 58 54 55", "M46 55 Q50 60 54 55", "M46 55 Q50 58 54 55"] } : {}}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
        
        {/* Tail (visible behind) */}
        <motion.path
          d="M75 65 Q85 55 80 45 Q75 50 70 60"
          stroke="#14B8A6"
          strokeWidth="6"
          fill="none"
          strokeLinecap="round"
          animate={isActive ? { 
            d: [
              "M75 65 Q85 55 80 45 Q75 50 70 60",
              "M75 65 Q90 50 85 40 Q80 45 70 60",
              "M75 65 Q85 55 80 45 Q75 50 70 60"
            ]
          } : {}}
          transition={{ duration: 1, repeat: Infinity, ease: 'easeInOut' }}
        />
      </svg>
      
      {/* Active indicator */}
      {isActive && (
        <motion.div
          className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full"
          animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
}