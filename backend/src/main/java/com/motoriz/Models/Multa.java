package com.motoriz.Models;

import com.motoriz.Enums.MultaStatusPagamento;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "multas")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Multa {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "veiculo_id", nullable = false)
    private Veiculo veiculo;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "locacao_id")
    private Locacao locacao;

    @Column(name = "codigo_infracao", length = 50)
    private String codigoInfracao;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal valor;

    @Column(name = "data_infracao", nullable = false)
    private LocalDateTime dataInfracao;

    @Enumerated(EnumType.STRING)
    @Column(name = "status_pagamento", nullable = false)
    @Builder.Default
    private MultaStatusPagamento statusPagamento = MultaStatusPagamento.PENDENTE;
}