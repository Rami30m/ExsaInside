"use client";
import Draggable from 'react-draggable';
import { useState } from "react";
import Input from "./components/input";
import ResultList from "./components/resultlist";

export default function Home() {
  const [results, setResults] = useState([]);

  const handleResultsUpdate = (newResults) => {
    setResults(newResults);
  };

  return (
    <div className="font-sans bg-[#282828]   min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <div className="items-center justify-items-center">
        <Input onResultsUpdate={handleResultsUpdate} />
      </div>
    
      {/* <Draggable handle=".xai-header" bounds="parent" defaultPosition={{ x: 100, y: 100 }}>
        
      </Draggable> */}
      <div className="mt-10">
        
        {/* <ResultList results={results} /> */}
        {results && <ResultList results={results} />}
      </div>
      
    </div>
  );
}
