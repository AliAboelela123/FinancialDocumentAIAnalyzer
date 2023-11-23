import React, { useState, useEffect, useRef } from 'react';
import {
  Button, TextField, Box, styled, Typography, IconButton, Paper
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PublishIcon from '@mui/icons-material/Publish';
import CloseIcon from '@mui/icons-material/Close';
import CircularProgress from '@mui/material/CircularProgress';

const StyledBox = styled(Box)({
  display: 'flex',
  justifyContent: 'space-between',
  padding: '1rem 0',
  backgroundColor: '#f3f3f3',
  borderTop: '1px solid #e0e0e0',
  position: 'fixed',
  width: '100%',
  bottom: 0,
  left: 0,
});

const StyledButton = styled(Button)({
  padding: '0.5rem 1rem',
  backgroundColor: '#B76E79',
  borderRadius: '0.5rem',
  color: 'white',
  marginRight: '1rem',
  fontFamily: 'Poppins, sans-serif',
  fontWeight: 600,
  '&:hover': {
    backgroundColor: '#0056b3',
  },
  '&:active': {
    backgroundColor: '#003d80',
  },
});

const StyledTextField = styled(TextField)({
  flex: 1,
  backgroundColor: 'white',
  margin: '0 1rem',
  '& .MuiInputBase-root': {
    borderRadius: '0.5rem',
  },
});

const StyledIconButton = styled(IconButton)({
  color: '#B76E79',
  '&:hover': {
    backgroundColor: '#f4f4f4',
  },
});

const StyledPaper = styled(Paper)({
  marginTop: '1rem',
  padding: '0.5rem',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  maxWidth: '100%',
  overflow: 'hidden',
  whiteSpace: 'nowrap',
  textOverflow: 'ellipsis',
});

const StyledFileName = styled(Typography)({
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap',
});

const QueryBar = ({ addMessage, uploadPDF, clearPDF, uploadedPDFs, setUploadedPDFs, selectedLevel }) => {
  const [isLoading, setIsLoading] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const queryBarRef = useRef(null);

  useEffect(() => {
    const currentRef = textareaRef.current;

    const handleInput = () => {
      if (currentRef) {
        currentRef.style.height = 'auto';
        currentRef.style.height = `${currentRef.scrollHeight}px`;
      }
    };

    if (currentRef) {
      currentRef.addEventListener('input', handleInput);
    }

    return () => {
      if (currentRef) {
        currentRef.removeEventListener('input', handleInput);
      }
    };
  }, []);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      uploadPDF(files[0]);
    }
  };

  const handleSendClick = async () => {
    if (textareaRef.current.value.trim() === '') {
      alert('Please Enter a Query.');
      return;
    }
    
    setIsLoading(true);

    try {
      // FormData to hold Text Query and PDF Files
      const formData = new FormData();

      // Append Text Query to formData
      formData.append('query', textareaRef.current.value.trim());
      formData.append('complexity', selectedLevel || 'Expert');

      // Check if there are any PDF files uploaded
      const hasPDFs = uploadedPDFs.length > 0;
    
      // Append each PDF File to formData only if there are PDF files
      if (hasPDFs) {
        uploadedPDFs.forEach((file) => {
          formData.append('pdfFiles', file, file.name);
        });
      }

      const response = await fetch('http://127.0.0.1:5001/query', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        
        const queryMessage = {
          type: 'query',
          text: `${textareaRef.current.value}${hasPDFs ? `\n${uploadedPDFs.map(file => file.name).join(', ')}` : ''}`,
        };
        const responseMessage = {
          type: 'response',
          text: data.response,
        };
        
        addMessage(queryMessage);
        addMessage(responseMessage);
      } else {
        throw new Error('Server Responded with an Error.');
      }
    } catch (error) {
      addMessage({ type: 'query', text: `Error Sending Message: ${textareaRef.current.value}` });
      addMessage({ type: 'response', text: `Error: ${error.message}` });
    } finally {
      setIsLoading(false);
      textareaRef.current.value = '';
      setUploadedPDFs([]);
    }
  };

  return (
    <Box ref={queryBarRef}>
      <StyledBox>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <StyledTextField
            multiline
            placeholder="Type your Query here..."
            inputRef={textareaRef}
            disabled={isLoading}
          />
          <Box display="flex" flexDirection="column" alignItems="start" pl={2} mt={1}>
            {uploadedPDFs.map((file, index) => (
              <StyledPaper key={index}>
                <StyledFileName variant="body2" title={file.name}>
                  {file.name}
                </StyledFileName>
                <StyledIconButton size="small" onClick={() => clearPDF(index)} disabled={isLoading}>
                  <CloseIcon />
                </StyledIconButton>
              </StyledPaper>
            ))}
          </Box>
        </Box>
        <StyledButton variant="contained" endIcon={<PublishIcon />} onClick={handleUploadClick} disabled={isLoading}>
          <Typography variant="button">Upload PDF</Typography>
        </StyledButton>
        <StyledButton
          variant="contained"
          endIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
          onClick={handleSendClick}
          disabled={isLoading}
        >
          <Typography variant="button">{isLoading ? 'Sending...' : 'Send'}</Typography>
        </StyledButton>
      </StyledBox>
      <input
        type="file"
        accept="application/pdf"
        style={{ display: 'none' }}
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        disabled={isLoading}
      />
    </Box>
  );
};

export default QueryBar;