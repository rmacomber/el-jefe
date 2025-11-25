import React from 'react';
import { Box, Typography } from '@mui/material';
import { StatusIndicatorProps } from '@/types';

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  pulse = false,
  size = 'medium',
  className,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'running':
        return 'success.main';
      case 'offline':
        return 'error.main';
      case 'warning':
      case 'paused':
        return 'warning.main';
      case 'error':
      case 'failed':
        return 'error.main';
      default:
        return 'grey.500';
    }
  };

  const getStatusSize = (size: 'small' | 'medium' | 'large') => {
    switch (size) {
      case 'small':
        return 8;
      case 'medium':
        return 12;
      case 'large':
        return 16;
      default:
        return 12;
    }
  };

  const indicatorSize = getStatusSize(size);
  const color = getStatusColor(status);

  return (
    <Box
      className={className}
      display="flex"
      alignItems="center"
      gap={1}
    >
      <Box
        sx={{
          width: indicatorSize,
          height: indicatorSize,
          borderRadius: '50%',
          backgroundColor: color,
          ...(pulse && {
            animation: 'pulse 2s infinite',
          }),
        }}
      />
      {size !== 'small' && (
        <Typography
          variant="caption"
          sx={{
            color: color,
            fontWeight: 500,
            textTransform: 'uppercase',
          }}
        >
          {status}
        </Typography>
      )}

      <style jsx>{`
        @keyframes pulse {
          0% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
          100% {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>
    </Box>
  );
};

export default StatusIndicator;