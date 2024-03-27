import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const stages = [
  { progress: 10, message: "Sending PDF to Server..." },
  { progress: 20, message: "Extracting PDF..." },
  { progress: 30, message: "Analyzing PDF..." },
  { progress: 60, message: "Calculating Embeddings..." },
  { progress: 80, message: "Preparing Query to be sent to LLM..." },
  { progress: 90, message: "Query sent to LLM, awaiting LLM response..." }
];

const LoadingScreen = ({ isLoading, timerDuration = 10000 }) => {
  const [currentMessage, setCurrentMessage] = useState(stages[0].message);

  useEffect(() => {
    if (isLoading) {
      const interval = timerDuration / stages.length;

      const updateMessage = (stageIndex) => {
        if (stageIndex < stages.length) {
          setCurrentMessage(stages[stageIndex].message);
          setTimeout(() => updateMessage(stageIndex + 1), interval);
        }
      };

      const timer = setTimeout(() => updateMessage(1), interval);

      return () => clearTimeout(timer);
    }
  }, [isLoading, timerDuration]);

  if (!isLoading) return null;

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      width="100vw"
      height="100vh"
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      bgcolor="rgba(255, 255, 255, 0.7)"
      zIndex="modal"
    >
      <CircularProgress color="inherit" />
      <Typography marginTop={2}>{currentMessage}</Typography>
    </Box>
  );
};

export default LoadingScreen;
