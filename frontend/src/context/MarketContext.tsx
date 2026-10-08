import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { MarketType } from '../types';

interface MarketContextType {
  market: MarketType;
  setMarket: (market: MarketType) => void;
  currencySymbol: string;
  currencyCode: string;
  salaryUnit: string;
  isUSA: boolean;
  isIndia: boolean;
  formatSalary: (val: number, options?: { isLpa?: boolean; includeUnit?: boolean }) => string;
}

const MarketContext = createContext<MarketContextType | undefined>(undefined);

export const MarketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [market, setMarketState] = useState<MarketType>(() => {
    const saved = localStorage.getItem('jobintel_market');
    return (saved === 'USA' || saved === 'India') ? saved : 'USA';
  });

  const setMarket = (newMarket: MarketType) => {
    setMarketState(newMarket);
    localStorage.setItem('jobintel_market', newMarket);
  };

  const isUSA = market === 'USA';
  const isIndia = market === 'India';
  const currencySymbol = isUSA ? '$' : '₹';
  const currencyCode = isUSA ? 'USD' : 'INR';
  const salaryUnit = isUSA ? 'Annual Base ($ USD)' : 'LPA (₹ Lakhs Per Annum)';

  const formatSalary = (
    val: number,
    options: { isLpa?: boolean; includeUnit?: boolean } = {}
  ): string => {
    const { isLpa = isIndia, includeUnit = true } = options;
    if (isUSA) {
      const formatted = `$${Math.round(val).toLocaleString()}`;
      return includeUnit ? formatted : `$${Math.round(val).toLocaleString()}`;
    } else {
      // India formatting
      if (isLpa) {
        return `₹${val.toFixed(2)} LPA`;
      } else {
        // Raw INR amount
        return `₹${Math.round(val).toLocaleString('en-IN')}`;
      }
    }
  };

  return (
    <MarketContext.Provider
      value={{
        market,
        setMarket,
        currencySymbol,
        currencyCode,
        salaryUnit,
        isUSA,
        isIndia,
        formatSalary,
      }}
    >
      {children}
    </MarketContext.Provider>
  );
};

export const useMarket = (): MarketContextType => {
  const context = useContext(MarketContext);
  if (!context) {
    throw new Error('useMarket must be used within a MarketProvider');
  }
  return context;
};
