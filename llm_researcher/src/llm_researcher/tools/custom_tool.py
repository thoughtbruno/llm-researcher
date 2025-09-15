from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import os


class OptimizedCSVAnalysisInput(BaseModel):
    """Input schema for OptimizedCSVAnalysis."""
    analysis_type: str = Field(
        default="overview", 
        description="Type of analysis: 'overview', 'productivity_stats', 'department_analysis', 'time_trends', 'correlation_analysis'"
    )


class RawDataAccessInput(BaseModel):
    """Input schema for RawDataAccess."""
    data_format: str = Field(
        default="sample", 
        description="Format to return data: 'sample' (first 50 rows), 'full' (all data), 'columns' (column info), 'summary' (basic stats)"
    )


class RawDataAccessTool(BaseTool):
    name: str = "Raw Data Access"
    description: str = (
        "Ferramenta otimizada que fornece acesso direto aos dados brutos do dataset de produtividade. "
        "Permite ao agente examinar os dados completos para fazer suas próprias análises e conclusões. "
        "Muito mais rápida que ler arquivo linha por linha."
    )
    args_schema: Type[BaseModel] = RawDataAccessInput

    def _load_data(self):
        """Load CSV data for analysis."""
        csv_path = 'knowledge/garments_worker_productivity.csv'
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                # Convert date column to datetime for better analysis
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return None
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None

    def _run(self, data_format: str = "sample") -> str:
        df = self._load_data()
        if df is None:
            return "Erro: Não foi possível carregar o dataset de produtividade."

        try:
            if data_format == "columns":
                return self._get_column_info(df)
            elif data_format == "sample":
                return self._get_sample_data(df)
            elif data_format == "full":
                return self._get_full_data(df)
            elif data_format == "summary":
                return self._get_basic_summary(df)
            else:
                return self._get_sample_data(df)
        except Exception as e:
            return f"Erro ao acessar dados: {str(e)}"

    def _get_column_info(self, df: pd.DataFrame) -> str:
        """Get information about columns and data types."""
        info = []
        info.append(f"INFORMAÇÕES DAS COLUNAS ({len(df.columns)} colunas, {len(df)} registros):\n")
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            
            if df[col].dtype in ['int64', 'float64']:
                min_val = df[col].min()
                max_val = df[col].max()
                info.append(f"• {col}: {dtype} | Nulos: {null_count} | Únicos: {unique_count} | Range: {min_val}-{max_val}")
            else:
                sample_values = df[col].value_counts().head(3).index.tolist()
                info.append(f"• {col}: {dtype} | Nulos: {null_count} | Únicos: {unique_count} | Exemplos: {sample_values}")
        
        return "\n".join(info)

    def _get_sample_data(self, df: pd.DataFrame) -> str:
        """Get first 50 rows of data for analysis."""
        sample_df = df.head(50)
        
        result = f"AMOSTRA DOS DADOS (primeiras 50 linhas de {len(df)} total):\n\n"
        result += "COLUNAS: " + " | ".join(df.columns.tolist()) + "\n\n"
        
        # Convert to string representation that's readable
        for idx, row in sample_df.iterrows():
            row_data = []
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    row_data.append("N/A")
                else:
                    row_data.append(str(value))
            result += f"Linha {idx+1}: " + " | ".join(row_data) + "\n"
        
        result += f"\n... (mostrando 50 de {len(df)} registros totais)\n"
        result += f"\nPara ver todos os dados, use data_format='full'"
        
        return result

    def _get_full_data(self, df: pd.DataFrame) -> str:
        """Get all data - use carefully as this can be very large."""
        if len(df) > 500:
            return f"ATENÇÃO: Dataset tem {len(df)} registros. Isso pode ser muito grande para processar de uma vez. Use 'sample' para ver uma amostra ou 'summary' para estatísticas básicas."
        
        result = f"DATASET COMPLETO ({len(df)} registros):\n\n"
        result += "COLUNAS: " + " | ".join(df.columns.tolist()) + "\n\n"
        
        # Convert to string representation
        for idx, row in df.iterrows():
            row_data = []
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    row_data.append("N/A")
                else:
                    row_data.append(str(value))
            result += f"Linha {idx+1}: " + " | ".join(row_data) + "\n"
        
        return result

    def _get_basic_summary(self, df: pd.DataFrame) -> str:
        """Get basic summary statistics."""
        result = f"RESUMO BÁSICO DO DATASET:\n\n"
        result += f"• Total de registros: {len(df)}\n"
        result += f"• Total de colunas: {len(df.columns)}\n"
        result += f"• Período: {df['date'].min()} a {df['date'].max()}\n\n"
        
        result += "ESTATÍSTICAS DAS COLUNAS NUMÉRICAS:\n"
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            stats = df[col].describe()
            result += f"\n{col}:\n"
            result += f"  Média: {stats['mean']:.3f}\n"
            result += f"  Mediana: {stats['50%']:.3f}\n"
            result += f"  Min: {stats['min']:.3f} | Max: {stats['max']:.3f}\n"
            result += f"  Desvio padrão: {stats['std']:.3f}\n"
        
        result += "\nCONTAGEM POR VALORES ÚNICOS (colunas categóricas):\n"
        categorical_cols = df.select_dtypes(exclude=[np.number, 'datetime64[ns]']).columns
        for col in categorical_cols:
            if col != 'date':  # Skip date column
                value_counts = df[col].value_counts()
                result += f"\n{col}: {value_counts.to_dict()}\n"
        
        return result


class OptimizedCSVAnalysisTool(BaseTool):
    name: str = "Optimized CSV Data Analysis"
    description: str = (
        "Ferramenta otimizada para análise rápida do dataset de produtividade. "
        "Fornece insights estatísticos específicos, correlações e tendências "
        "com dados numéricos precisos. Muito mais rápida que ler o arquivo linha por linha."
    )
    args_schema: Type[BaseModel] = OptimizedCSVAnalysisInput

    def _load_data(self):
        """Load CSV data for analysis."""
        csv_path = 'knowledge/garments_worker_productivity.csv'
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                # Convert date column to datetime for better analysis
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return None
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None

    def _run(self, analysis_type: str = "overview") -> str:
        df = self._load_data()
        if df is None:
            return "Erro: Não foi possível carregar o dataset de produtividade."

        try:
            if analysis_type == "overview":
                return self._get_overview(df)
            elif analysis_type == "productivity_stats":
                return self._get_productivity_stats(df)
            elif analysis_type == "department_analysis":
                return self._get_department_analysis(df)
            elif analysis_type == "time_trends":
                return self._get_time_trends(df)
            elif analysis_type == "correlation_analysis":
                return self._get_correlation_analysis(df)
            else:
                return self._get_overview(df)
        except Exception as e:
            return f"Erro na análise: {str(e)}"

    def _get_overview(self, df: pd.DataFrame) -> str:
        """Get comprehensive overview of the dataset."""
        total_records = len(df)
        date_range = f"{df['date'].min().strftime('%Y-%m-%d')} a {df['date'].max().strftime('%Y-%m-%d')}"
        
        # Basic statistics
        avg_productivity = df['actual_productivity'].mean()
        avg_target = df['targeted_productivity'].mean()
        productivity_gap = ((avg_productivity - avg_target) / avg_target) * 100
        
        departments = df['department'].value_counts()
        teams = df['team'].nunique()
        total_workers = df['no_of_workers'].sum()
        
        return f"""
VISÃO GERAL DO DATASET:
• Total de registros: {total_records:,}
• Período analisado: {date_range}
• Departamentos: {', '.join(departments.index.tolist())}
• Número de equipes: {teams}
• Total de trabalhadores: {total_workers:,}

MÉTRICAS DE PRODUTIVIDADE:
• Produtividade média alcançada: {avg_productivity:.3f} ({avg_productivity*100:.1f}%)
• Meta média de produtividade: {avg_target:.3f} ({avg_target*100:.1f}%)
• Gap de performance: {productivity_gap:+.1f}%

DISTRIBUIÇÃO POR DEPARTAMENTO:
{chr(10).join([f'• {dept}: {count:,} registros ({count/total_records*100:.1f}%)' for dept, count in departments.items()])}
        """

    def _get_productivity_stats(self, df: pd.DataFrame) -> str:
        """Get detailed productivity statistics."""
        productivity = df['actual_productivity']
        target = df['targeted_productivity']
        
        # Performance metrics
        above_target = (productivity > target).sum()
        below_target = (productivity < target).sum()
        at_target = (productivity == target).sum()
        
        # Statistical measures
        prod_stats = productivity.describe()
        
        # Efficiency analysis
        efficiency = productivity / target
        high_performers = (efficiency > 1.1).sum()  # 10% above target
        low_performers = (efficiency < 0.9).sum()   # 10% below target
        
        return f"""
ESTATÍSTICAS DETALHADAS DE PRODUTIVIDADE:

PERFORMANCE vs META:
• Acima da meta: {above_target:,} registros ({above_target/len(df)*100:.1f}%)
• Abaixo da meta: {below_target:,} registros ({below_target/len(df)*100:.1f}%)
• Na meta: {at_target:,} registros ({at_target/len(df)*100:.1f}%)

DISTRIBUIÇÃO DE PRODUTIVIDADE:
• Mínima: {prod_stats['min']:.3f} ({prod_stats['min']*100:.1f}%)
• 25º percentil: {prod_stats['25%']:.3f} ({prod_stats['25%']*100:.1f}%)
• Mediana: {prod_stats['50%']:.3f} ({prod_stats['50%']*100:.1f}%)
• Média: {prod_stats['mean']:.3f} ({prod_stats['mean']*100:.1f}%)
• 75º percentil: {prod_stats['75%']:.3f} ({prod_stats['75%']*100:.1f}%)
• Máxima: {prod_stats['max']:.3f} ({prod_stats['max']*100:.1f}%)
• Desvio padrão: {prod_stats['std']:.3f}

ANÁLISE DE EFICIÊNCIA:
• Alto desempenho (>110% da meta): {high_performers:,} registros ({high_performers/len(df)*100:.1f}%)
• Baixo desempenho (<90% da meta): {low_performers:,} registros ({low_performers/len(df)*100:.1f}%)
• Coeficiente de variação: {(prod_stats['std']/prod_stats['mean'])*100:.1f}%
        """

    def _get_department_analysis(self, df: pd.DataFrame) -> str:
        """Analyze productivity by department."""
        dept_analysis = df.groupby('department').agg({
            'actual_productivity': ['mean', 'std', 'min', 'max', 'count'],
            'targeted_productivity': 'mean',
            'no_of_workers': 'sum',
            'over_time': 'mean',
            'idle_time': 'mean'
        }).round(3)
        
        results = []
        for dept in dept_analysis.index:
            avg_prod = dept_analysis.loc[dept, ('actual_productivity', 'mean')]
            avg_target = dept_analysis.loc[dept, ('targeted_productivity', 'mean')]
            gap = ((avg_prod - avg_target) / avg_target) * 100
            workers = dept_analysis.loc[dept, ('no_of_workers', 'sum')]
            records = dept_analysis.loc[dept, ('actual_productivity', 'count')]
            overtime = dept_analysis.loc[dept, ('over_time', 'mean')]
            idle = dept_analysis.loc[dept, ('idle_time', 'mean')]
            
            results.append(f"""
DEPARTAMENTO: {dept.upper()}
• Registros: {records:,}
• Total de trabalhadores: {workers:,}
• Produtividade média: {avg_prod:.3f} ({avg_prod*100:.1f}%)
• Meta média: {avg_target:.3f} ({avg_target*100:.1f}%)
• Gap de performance: {gap:+.1f}%
• Horas extras médias: {overtime:.1f}h
• Tempo ocioso médio: {idle:.1f}min
            """)
        
        return "ANÁLISE POR DEPARTAMENTO:" + "".join(results)

    def _get_time_trends(self, df: pd.DataFrame) -> str:
        """Analyze productivity trends over time."""
        # Monthly trends
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        
        monthly_prod = df.groupby('month')['actual_productivity'].mean()
        daily_prod = df.groupby('day_of_week')['actual_productivity'].mean()
        
        # Quarter analysis
        quarter_prod = df.groupby('quarter')['actual_productivity'].mean()
        
        best_month = monthly_prod.idxmax()
        worst_month = monthly_prod.idxmin()
        best_day = daily_prod.idxmax()
        worst_day = daily_prod.idxmin()
        
        return f"""
TENDÊNCIAS TEMPORAIS:

ANÁLISE POR TRIMESTRE:
{chr(10).join([f'• {quarter}: {prod:.3f} ({prod*100:.1f}%)' for quarter, prod in quarter_prod.items()])}

ANÁLISE MENSAL:
• Melhor mês: {best_month} com {monthly_prod[best_month]:.3f} ({monthly_prod[best_month]*100:.1f}%)
• Pior mês: {worst_month} com {monthly_prod[worst_month]:.3f} ({monthly_prod[worst_month]*100:.1f}%)
• Variação mensal: {(monthly_prod.max() - monthly_prod.min()):.3f} ({(monthly_prod.max() - monthly_prod.min())*100:.1f} pontos percentuais)

ANÁLISE POR DIA DA SEMANA:
• Melhor dia: {best_day} com {daily_prod[best_day]:.3f} ({daily_prod[best_day]*100:.1f}%)
• Pior dia: {worst_day} com {daily_prod[worst_day]:.3f} ({daily_prod[worst_day]*100:.1f}%)
{chr(10).join([f'• {day}: {prod:.3f} ({prod*100:.1f}%)' for day, prod in daily_prod.sort_values(ascending=False).items()])}
        """

    def _get_correlation_analysis(self, df: pd.DataFrame) -> str:
        """Analyze correlations between variables."""
        # Select numerical columns for correlation
        numerical_cols = ['actual_productivity', 'targeted_productivity', 'smv', 'over_time', 
                         'idle_time', 'no_of_workers', 'no_of_style_change', 'incentive']
        
        corr_matrix = df[numerical_cols].corr()['actual_productivity'].sort_values(ascending=False)
        
        strong_correlations = []
        for var, corr in corr_matrix.items():
            if var != 'actual_productivity' and abs(corr) > 0.1:
                direction = "positiva" if corr > 0 else "negativa"
                strength = "forte" if abs(corr) > 0.5 else "moderada" if abs(corr) > 0.3 else "fraca"
                strong_correlations.append(f"• {var}: {corr:.3f} (correlação {strength} {direction})")
        
        return f"""
ANÁLISE DE CORRELAÇÕES COM PRODUTIVIDADE:

CORRELAÇÕES IDENTIFICADAS:
{chr(10).join(strong_correlations)}

INSIGHTS:
• Variáveis com maior impacto positivo: {corr_matrix[corr_matrix > 0.1].head(3).index.tolist()}
• Variáveis com maior impacto negativo: {corr_matrix[corr_matrix < -0.1].head(3).index.tolist()}
        """
