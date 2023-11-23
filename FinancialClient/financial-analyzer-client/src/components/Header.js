import React from 'react';
import { Box, Typography, styled } from '@mui/material';
import Dropdown from './Dropdown';
import { GlobalStyles } from '@mui/system';

const StyledHeader = styled(Box)(({ theme }) => ({
  backgroundColor: '#2C3E50',
  color: 'white',
  textAlign: 'center',
  position: 'fixed',
  width: '100%',
  top: 0,
  left: 0,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
}));

const Header = ({ selectedLevel, setSelectedLevel }) => {
  return (
    <StyledHeader>
      <GlobalStyles styles={{
        '@global': {
          '@font-face': {
            fontFamily: 'Poppins',
            src: `url(https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap)`,
          },
          body: {
            fontFamily: 'Poppins, sans-serif',
          },
        },
      }} />
      <Typography variant="h6" style={{ marginLeft: 20, marginTop: 10, marginBottom: 10, fontFamily: "Poppins", fontWeight: 600 }}>Financial LLM Analyzer</Typography>
      <Dropdown selectedLevel={selectedLevel} setSelectedLevel={setSelectedLevel} />
    </StyledHeader>
  );
};

export default Header;
