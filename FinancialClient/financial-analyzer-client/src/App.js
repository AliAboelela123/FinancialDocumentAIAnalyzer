import React, { useState } from 'react';
import Header from './components/Header';
import MainContent from './components/MainContent';
import QueryBar from './components/QueryBar';
import PDFViewer from './components/PDFViewer';
import { Box, createTheme, ThemeProvider } from '@mui/material';
import './App.css';

const theme = createTheme({
  typography: {
    fontFamily: 'Poppins, sans-serif',
  },
});

const App = () => {
  const [messages, setMessages] = useState([]);
  const [uploadedPDFs, setUploadedPDFs] = useState([]);
  const [selectedLevel, setSelectedLevel] = useState('Beginner');

  const [isPdfOpen, setIsPdfOpen] = useState(false);
  const [selectedPdf, setSelectedPdf] = useState(null);

  const handleOpenPdf = (pdfFile) => {
    setSelectedPdf(pdfFile);
    setIsPdfOpen(true);
  };

  const handleClosePdf = () => {
    setIsPdfOpen(false);
    setSelectedPdf(null);
  };

  const addMessage = (newMessage) => {
    setMessages((prevMessages) => {
      const updatedMessages = [...prevMessages, newMessage];
      console.log(updatedMessages);
      return updatedMessages;
    });
  };

  const appendMessage = (additionalText) => {
    setMessages((prevMessages) => {
      if (prevMessages.length === 0) {
        return prevMessages;
      }

      const lastMessage = { ...prevMessages[prevMessages.length - 1] };

      if (lastMessage.type === 'response') {
        lastMessage.text += additionalText;
      }

      return [...prevMessages.slice(0, -1), lastMessage];
    });
  };

  const uploadPDF = (file) => {
    setUploadedPDFs(uploadedPDFs => [...uploadedPDFs, file]);
  };

  const clearPDF = (index) => {
    setUploadedPDFs(uploadedPDFs.filter((_, i) => i !== index));
  };

  console.log('Rendering App Component with Messages:', messages);

  return (
    <ThemeProvider theme={theme}>
      <div className="app">
        <Header selectedLevel={selectedLevel} setSelectedLevel={setSelectedLevel} />
        <Box sx={{ display: 'flex', width: '100%', height: '81%' }}>
          <MainContent messages={messages} onOpenPdf={handleOpenPdf} />
          {isPdfOpen && (
            <Box sx={{ width: '50%' }}>
              <PDFViewer pdfFile={selectedPdf} onClose={handleClosePdf} />
            </Box>
          )}
        </Box>
        <QueryBar
          addMessage={addMessage}
          appendMessage={appendMessage}
          uploadPDF={uploadPDF}
          clearPDF={clearPDF}
          uploadedPDFs={uploadedPDFs}
          setUploadedPDFs={setUploadedPDFs}
          selectedLevel={selectedLevel}
        />
      </div>
    </ThemeProvider>
  );
};

export default App;