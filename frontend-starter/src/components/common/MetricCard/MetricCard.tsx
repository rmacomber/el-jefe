import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import { MetricCardProps } from '@/types';

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType,
  icon,
  loading = false,
  className,
}) => {
  const getTrendIcon = (type?: 'increase' | 'decrease') => {
    switch (type) {
      case 'increase':
        return <TrendingUp sx={{ color: 'success.main', fontSize: 16 }} />;
      case 'decrease':
        return <TrendingDown sx={{ color: 'error.main', fontSize: 16 }} />;
      default:
        return <TrendingFlat sx={{ color: 'grey.500', fontSize: 16 }} />;
    }
  };

  const getTrendColor = (type?: 'increase' | 'decrease') => {
    switch (type) {
      case 'increase':
        return 'success.main';
      case 'decrease':
        return 'error.main';
      default:
        return 'grey.500';
    }
  };

  const formatValue = (val: number | string) => {
    if (typeof val === 'number') {
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <Card
      className={className}
      sx={{
        height: '100%',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: (theme) => theme.shadows[8],
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" color="text.secondary" fontWeight={500}>
            {title}
          </Typography>
          {icon && (
            <Box sx={{ color: 'primary.main', opacity: 0.8 }}>
              {icon}
            </Box>
          )}
        </Box>

        {loading ? (
          <Box>
            <Box
              sx={{
                height: 40,
                backgroundColor: 'grey.200',
                borderRadius: 1,
                mb: 1,
                animation: 'pulse 1.5s infinite',
              }}
            />
            <Box
              sx={{
                height: 24,
                backgroundColor: 'grey.200',
                borderRadius: 1,
                width: '60%',
                animation: 'pulse 1.5s infinite',
              }}
            />
          </Box>
        ) : (
          <>
            <Typography
              variant="h3"
              component="div"
              fontWeight={700}
              sx={{
                background: 'linear-gradient(45deg, #667eea, #764ba2)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                mb: 1,
              }}
            >
              {formatValue(value)}
            </Typography>

            {change !== undefined && (
              <Box display="flex" alignItems="center" gap={1}>
                {getTrendIcon(changeType)}
                <Typography
                  variant="body2"
                  color={getTrendColor(changeType)}
                  fontWeight={500}
                >
                  {changeType === 'increase' ? '+' : ''}{change}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  from last period
                </Typography>
              </Box>
            )}

            {change === undefined && (
              <Typography variant="body2" color="text.secondary">
                Current value
              </Typography>
            )}
          </>
        )}
      </CardContent>

      <style jsx>{`
        @keyframes pulse {
          0% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
          100% {
            opacity: 1;
          }
        }
      `}</style>
    </Card>
  );
};

export default MetricCard;