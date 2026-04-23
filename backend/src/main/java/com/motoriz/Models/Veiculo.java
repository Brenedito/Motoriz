package com.motoriz.Models;

import com.motoriz.Enums.VeiculoStatus;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "veiculos")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Veiculo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, length = 50)
    private String modelo;

    @Column(nullable = false, length = 50)
    private String marca;

    @Column(nullable = false, unique = true, length = 10)
    private String placa;

    @Column(nullable = false)
    private Integer ano;

    @Column(length = 20)
    private String cor;

    @Column(name = "quilometragem_atual")
    @Builder.Default
    private Integer quilometragemAtual = 0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private VeiculoStatus status = VeiculoStatus.DISPONIVEL;

    @Column(name = "localizacao_atual", length = 100)
    @Builder.Default
    private String localizacaoAtual = "Pátio Central";

    @Column(name = "km_proxima_revisao")
    private Integer kmProximaRevisao;
}