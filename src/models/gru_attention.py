"""
Comprehensive Research Model Suite:
Supports:
1. Baseline GRU (multi-task & single-task)
2. Baseline LSTM (for RNN family comparison)
3. GRU + Temporal Attention (Single-head scaled dot-product)
4. Full Proposed: GRU + Temporal Attention + Stress Features
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class SingleHeadTemporalAttention(nn.Module):
    """
    Scaled Dot-Product Temporal Attention over sequential cycle representations.
    Computes data-dependent importance weights over historical cycles without overfitting.
    """
    def __init__(self, hidden_dim):
        super(SingleHeadTemporalAttention, self).__init__()
        self.query_proj = nn.Linear(hidden_dim, hidden_dim)
        self.key_proj = nn.Linear(hidden_dim, hidden_dim)
        self.val_proj = nn.Linear(hidden_dim, hidden_dim)
        self.scale = 1.0 / math.sqrt(hidden_dim)

    def forward(self, x):
        # x: (Batch, Seq_Len, Hidden_Dim)
        q = self.query_proj(x)
        k = self.key_proj(x)
        v = self.val_proj(x)
        
        scores = torch.bmm(q, k.transpose(1, 2)) * self.scale
        weights = F.softmax(scores, dim=-1) # (Batch, Seq_Len, Seq_Len)
        out = torch.bmm(weights, v)
        return out, weights

class BatteryHealthModel(nn.Module):
    """
    Modular Battery Health Neural Architecture.
    Can be configured as:
      - rnn_type: 'GRU' or 'LSTM'
      - use_attention: True / False
      - task_mode: 'multi_task', 'soh_only', 'rul_only'
    """
    def __init__(self, input_dim, hidden_dim=48, num_layers=2, rnn_type='GRU', use_attention=True, task_mode='multi_task', dropout=0.15):
        super(BatteryHealthModel, self).__init__()
        self.rnn_type = rnn_type
        self.use_attention = use_attention
        self.task_mode = task_mode
        
        if rnn_type == 'LSTM':
            self.rnn = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0.0
            )
        else:
            self.rnn = nn.GRU(
                input_size=input_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0.0
            )
            
        if use_attention:
            self.attention = SingleHeadTemporalAttention(hidden_dim)
            self.norm = nn.LayerNorm(hidden_dim)
            
        self.shared_dense = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # SOH Output Head
        if task_mode in ['multi_task', 'soh_only']:
            self.soh_head = nn.Sequential(
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, 1)
            )
        else:
            self.soh_head = None
            
        # RUL Output Head
        if task_mode in ['multi_task', 'rul_only']:
            self.rul_head = nn.Sequential(
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, 1),
                nn.ReLU()
            )
        else:
            self.rul_head = None

    def forward(self, x):
        if self.rnn_type == 'LSTM':
            rnn_out, _ = self.rnn(x)
        else:
            rnn_out, _ = self.rnn(x)
            
        if self.use_attention:
            attn_out, weights = self.attention(rnn_out)
            context = self.norm(rnn_out[:, -1, :] + attn_out[:, -1, :])
        else:
            context = rnn_out[:, -1, :]
            weights = None
            
        shared = self.shared_dense(context)
        soh_pred = self.soh_head(shared) if self.soh_head is not None else None
        rul_pred = self.rul_head(shared) if self.rul_head is not None else None
        
        return soh_pred, rul_pred, weights

# Backward compatibility alias
BatteryGRUAttention = BatteryHealthModel
