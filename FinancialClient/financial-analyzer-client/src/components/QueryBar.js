import React, { useState, useEffect, useRef } from 'react';
import {
  Button, TextField, Box, styled, Typography, IconButton, Paper, Checkbox, FormControlLabel
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

const QueryBar = ({ addMessage, appendMessage, uploadPDF, clearPDF, uploadedPDFs, setUploadedPDFs, selectedLevel, setIsLoadingApp, setLoadingDuration }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showReferences, setShowReferences] = useState(false);
  const [showTables, setShowTables] = useState(false);

  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const queryBarRef = useRef(null);

  const handleCheckboxChange = (event) => {
    if (event.target.name === "showReferences") {
      setShowReferences(event.target.checked);
    } else if (event.target.name === "showTables") {
      setShowTables(event.target.checked);
    }
  };

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
    event.target.value = '';
  };

  const handleSendClick = async () => {
    if (textareaRef.current.value.trim() === '') {
      alert('Please Enter a Query.');
      return;
    }

    const queryMessage = {
      type: 'query',
      text: `${textareaRef.current.value}`,
      files: uploadedPDFs.map(file => URL.createObjectURL(file)),
      fileName: uploadedPDFs.map(file => file.name)
    };

    addMessage(queryMessage);
  
    setIsLoading(true);
    setIsLoadingApp(true);
    
    //TODO: Calculate TIME, value is in Milliseconds :D
    setLoadingDuration(20000);
    let isFirstChunk = true;

    try {
      // FormData to hold Text Query and PDF Files
      const formData = new FormData();
  
      // Append Text Query and complexity to formData
      formData.append('query', textareaRef.current.value.trim());
      formData.append('complexity', selectedLevel || 'Expert');
  
      // Append PDF Files to formData
      uploadedPDFs.forEach((file) => {
        formData.append('pdfFiles', file, file.name);
      });
  
      const controller = new AbortController();
      const signal = controller.signal;
      const response = await fetch('http://127.0.0.1:5001/query', {
        method: 'POST',
        body: formData,
        signal: signal,
      });
      
      if (response.ok) {

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let result = '';
  
        const read = async () => {
          const { done, value } = await reader.read();
          if (done) {
            setIsLoading(false);
            setIsLoadingApp(false);
            if (showReferences) fetchReferences();
            if (showTables) fetchTables();
            return;
          }
          result += decoder.decode(value, { stream: true });
  
          // Process Each Chunk
          try {
            if (result.endsWith('\n\n')) {
              const jsons = result.trim().split('\n\n');
              jsons.forEach(json => {
                const parsed = JSON.parse(json);

                if (parsed.data || parsed.error) {
                  if (isFirstChunk || parsed.error) {
                    const messageText = parsed.error || parsed.data;

                    addMessage({ type: 'response', text: messageText });
                    isFirstChunk = false;
                  } else {
                    appendMessage(parsed.data);
                  }
                }
              });
              result = '';
            }
          } catch (e) {
            console.error(e);
          }
  
          read();
        };
  
        read();
      } else {
        throw new Error('Server Responded with an Error.');
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
    } finally {
      textareaRef.current.value = '';
      setUploadedPDFs([]);
      setIsLoading(false);
      setIsLoadingApp(false);
      
    }
  };

  const fetchReferences = async () => {
    try {
      const referencesResponse = await fetch('http://127.0.0.1:5001/references');
      if (!referencesResponse.ok) {
        throw new Error('Error Fetching References.');
      }
  
      const referencesData = await referencesResponse.json();
      if (referencesData.error) {
        console.error('Error in References Data:', referencesData.error);
      } else {
        referencesData.references.map((reference) => {
          addMessage({ type: 'response', text: "Value **" + reference[0] + "**, found in **" + reference[1] +  "** in PDF "+ reference[2] });
        });
      }
    } catch (error) {
      console.error(`Error Fetching References: ${error}`);
    } finally {
      setIsLoading(false);
      setIsLoadingApp(false);
      textareaRef.current.value = '';
      setUploadedPDFs([]);

    }
  };

  const fetchTables = async () => {
    try {
      const tableResponse = await fetch('http://127.0.0.1:5001/extractedTable');
      if (!tableResponse.ok) {
        throw new Error('Error Fetching Tables.');
      }
  
      const tableData = await tableResponse.json();
      if (tableData.error) {
        console.error('Error in Table Data:', tableData.error);
      } else {
        if (tableData.extractedTable.includes('!')) {
          addMessage({ type: 'response', text: tableData.extractedTable });
        }
      }
    } catch (error) {
      console.error(`Error Fetching Data: ${error}`);
    } finally {
      setIsLoading(false);
      setIsLoadingApp(false);
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
        <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
          <FormControlLabel
            sx ={{ marginTop: -1 }}
            control={
              <Checkbox
                checked={showReferences}
                onChange={handleCheckboxChange}
                name="showReferences"
              />
            }
            label="Include References"
          />
          <FormControlLabel
            sx ={{ marginTop: -2.5 }}
            control={
              <Checkbox
                checked={showTables}
                onChange={handleCheckboxChange}
                name="showTables"
              />
            }
            label="Include Tables"
          />
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