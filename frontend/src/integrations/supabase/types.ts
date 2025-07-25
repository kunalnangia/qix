export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instanciate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.3 (519615d)"
  }
  public: {
    Tables: {
      ai_test_generation_requests: {
        Row: {
          created_at: string | null
          created_by: string | null
          generated_tests: Json | null
          id: string
          project_id: string | null
          status: string | null
          user_input: string
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          generated_tests?: Json | null
          id?: string
          project_id?: string | null
          status?: string | null
          user_input: string
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          generated_tests?: Json | null
          id?: string
          project_id?: string | null
          status?: string | null
          user_input?: string
        }
        Relationships: [
          {
            foreignKeyName: "ai_test_generation_requests_created_by_fkey"
            columns: ["created_by"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ai_test_generation_requests_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      api_test_configs: {
        Row: {
          body: Json | null
          created_at: string | null
          endpoint: string
          expected_response: Json | null
          expected_status: number | null
          headers: Json | null
          id: string
          method: string
          test_case_id: string | null
        }
        Insert: {
          body?: Json | null
          created_at?: string | null
          endpoint: string
          expected_response?: Json | null
          expected_status?: number | null
          headers?: Json | null
          id?: string
          method: string
          test_case_id?: string | null
        }
        Update: {
          body?: Json | null
          created_at?: string | null
          endpoint?: string
          expected_response?: Json | null
          expected_status?: number | null
          headers?: Json | null
          id?: string
          method?: string
          test_case_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "api_test_configs_test_case_id_fkey"
            columns: ["test_case_id"]
            isOneToOne: false
            referencedRelation: "test_cases"
            referencedColumns: ["id"]
          },
        ]
      }
      performance_metrics: {
        Row: {
          cpu_usage: number | null
          created_at: string | null
          cumulative_layout_shift: number | null
          execution_id: string | null
          first_contentful_paint: number | null
          id: string
          largest_contentful_paint: number | null
          memory_usage: number | null
          network_requests: number | null
          page_load_time: number | null
          time_to_interactive: number | null
        }
        Insert: {
          cpu_usage?: number | null
          created_at?: string | null
          cumulative_layout_shift?: number | null
          execution_id?: string | null
          first_contentful_paint?: number | null
          id?: string
          largest_contentful_paint?: number | null
          memory_usage?: number | null
          network_requests?: number | null
          page_load_time?: number | null
          time_to_interactive?: number | null
        }
        Update: {
          cpu_usage?: number | null
          created_at?: string | null
          cumulative_layout_shift?: number | null
          execution_id?: string | null
          first_contentful_paint?: number | null
          id?: string
          largest_contentful_paint?: number | null
          memory_usage?: number | null
          network_requests?: number | null
          page_load_time?: number | null
          time_to_interactive?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "performance_metrics_execution_id_fkey"
            columns: ["execution_id"]
            isOneToOne: false
            referencedRelation: "test_executions"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          created_at: string | null
          email: string
          full_name: string | null
          id: string
          role: Database["public"]["Enums"]["user_role"] | null
          team_id: string | null
          updated_at: string | null
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string | null
          email: string
          full_name?: string | null
          id: string
          role?: Database["public"]["Enums"]["user_role"] | null
          team_id?: string | null
          updated_at?: string | null
        }
        Update: {
          avatar_url?: string | null
          created_at?: string | null
          email?: string
          full_name?: string | null
          id?: string
          role?: Database["public"]["Enums"]["user_role"] | null
          team_id?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      projects: {
        Row: {
          base_url: string | null
          created_at: string | null
          created_by: string | null
          description: string | null
          id: string
          name: string
          status: Database["public"]["Enums"]["test_status"] | null
          team_id: string | null
          updated_at: string | null
        }
        Insert: {
          base_url?: string | null
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          id?: string
          name: string
          status?: Database["public"]["Enums"]["test_status"] | null
          team_id?: string | null
          updated_at?: string | null
        }
        Update: {
          base_url?: string | null
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          id?: string
          name?: string
          status?: Database["public"]["Enums"]["test_status"] | null
          team_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "projects_created_by_fkey"
            columns: ["created_by"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "projects_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      security_scan_results: {
        Row: {
          created_at: string | null
          description: string | null
          id: string
          location: string | null
          remediation: string | null
          severity: Database["public"]["Enums"]["priority_level"] | null
          status: string | null
          test_case_id: string | null
          vulnerability_type: string | null
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          id?: string
          location?: string | null
          remediation?: string | null
          severity?: Database["public"]["Enums"]["priority_level"] | null
          status?: string | null
          test_case_id?: string | null
          vulnerability_type?: string | null
        }
        Update: {
          created_at?: string | null
          description?: string | null
          id?: string
          location?: string | null
          remediation?: string | null
          severity?: Database["public"]["Enums"]["priority_level"] | null
          status?: string | null
          test_case_id?: string | null
          vulnerability_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "security_scan_results_test_case_id_fkey"
            columns: ["test_case_id"]
            isOneToOne: false
            referencedRelation: "test_cases"
            referencedColumns: ["id"]
          },
        ]
      }
      teams: {
        Row: {
          created_at: string | null
          created_by: string | null
          description: string | null
          id: string
          name: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          id?: string
          name: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          id?: string
          name?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "teams_created_by_fkey"
            columns: ["created_by"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      test_cases: {
        Row: {
          actual_result: string | null
          ai_generated: boolean | null
          assigned_to: string | null
          created_at: string | null
          created_by: string | null
          description: string | null
          expected_result: string | null
          id: string
          priority: Database["public"]["Enums"]["priority_level"] | null
          project_id: string | null
          self_healing_enabled: boolean | null
          status: Database["public"]["Enums"]["test_status"] | null
          steps: Json | null
          tags: string[] | null
          test_type: Database["public"]["Enums"]["test_type"] | null
          title: string
          updated_at: string | null
        }
        Insert: {
          actual_result?: string | null
          ai_generated?: boolean | null
          assigned_to?: string | null
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          expected_result?: string | null
          id?: string
          priority?: Database["public"]["Enums"]["priority_level"] | null
          project_id?: string | null
          self_healing_enabled?: boolean | null
          status?: Database["public"]["Enums"]["test_status"] | null
          steps?: Json | null
          tags?: string[] | null
          test_type?: Database["public"]["Enums"]["test_type"] | null
          title: string
          updated_at?: string | null
        }
        Update: {
          actual_result?: string | null
          ai_generated?: boolean | null
          assigned_to?: string | null
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          expected_result?: string | null
          id?: string
          priority?: Database["public"]["Enums"]["priority_level"] | null
          project_id?: string | null
          self_healing_enabled?: boolean | null
          status?: Database["public"]["Enums"]["test_status"] | null
          steps?: Json | null
          tags?: string[] | null
          test_type?: Database["public"]["Enums"]["test_type"] | null
          title?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "test_cases_assigned_to_fkey"
            columns: ["assigned_to"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "test_cases_created_by_fkey"
            columns: ["created_by"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "test_cases_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      test_executions: {
        Row: {
          browser_info: Json | null
          completed_at: string | null
          created_at: string | null
          duration_ms: number | null
          error_message: string | null
          executed_by: string | null
          id: string
          logs: Json | null
          screenshots: string[] | null
          started_at: string | null
          status: Database["public"]["Enums"]["execution_status"] | null
          test_case_id: string | null
          test_plan_id: string | null
        }
        Insert: {
          browser_info?: Json | null
          completed_at?: string | null
          created_at?: string | null
          duration_ms?: number | null
          error_message?: string | null
          executed_by?: string | null
          id?: string
          logs?: Json | null
          screenshots?: string[] | null
          started_at?: string | null
          status?: Database["public"]["Enums"]["execution_status"] | null
          test_case_id?: string | null
          test_plan_id?: string | null
        }
        Update: {
          browser_info?: Json | null
          completed_at?: string | null
          created_at?: string | null
          duration_ms?: number | null
          error_message?: string | null
          executed_by?: string | null
          id?: string
          logs?: Json | null
          screenshots?: string[] | null
          started_at?: string | null
          status?: Database["public"]["Enums"]["execution_status"] | null
          test_case_id?: string | null
          test_plan_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "test_executions_executed_by_fkey"
            columns: ["executed_by"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "test_executions_test_case_id_fkey"
            columns: ["test_case_id"]
            isOneToOne: false
            referencedRelation: "test_cases"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "test_executions_test_plan_id_fkey"
            columns: ["test_plan_id"]
            isOneToOne: false
            referencedRelation: "test_plans"
            referencedColumns: ["id"]
          },
        ]
      }
      test_plan_cases: {
        Row: {
          created_at: string | null
          execution_order: number | null
          id: string
          test_case_id: string | null
          test_plan_id: string | null
        }
        Insert: {
          created_at?: string | null
          execution_order?: number | null
          id?: string
          test_case_id?: string | null
          test_plan_id?: string | null
        }
        Update: {
          created_at?: string | null
          execution_order?: number | null
          id?: string
          test_case_id?: string | null
          test_plan_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "test_plan_cases_test_case_id_fkey"
            columns: ["test_case_id"]
            isOneToOne: false
            referencedRelation: "test_cases"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "test_plan_cases_test_plan_id_fkey"
            columns: ["test_plan_id"]
            isOneToOne: false
            referencedRelation: "test_plans"
            referencedColumns: ["id"]
          },
        ]
      }
      test_plans: {
        Row: {
          browser_config: Json | null
          created_at: string | null
          created_by: string | null
          description: string | null
          environment: string | null
          id: string
          name: string
          project_id: string | null
          scheduled_date: string | null
          status: Database["public"]["Enums"]["test_status"] | null
          updated_at: string | null
        }
        Insert: {
          browser_config?: Json | null
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          environment?: string | null
          id?: string
          name: string
          project_id?: string | null
          scheduled_date?: string | null
          status?: Database["public"]["Enums"]["test_status"] | null
          updated_at?: string | null
        }
        Update: {
          browser_config?: Json | null
          created_at?: string | null
          created_by?: string | null
          description?: string | null
          environment?: string | null
          id?: string
          name?: string
          project_id?: string | null
          scheduled_date?: string | null
          status?: Database["public"]["Enums"]["test_status"] | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "test_plans_created_by_fkey"
            columns: ["created_by"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "test_plans_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      visual_baselines: {
        Row: {
          browser: string | null
          created_at: string | null
          id: string
          screenshot_url: string
          test_case_id: string | null
          viewport_height: number | null
          viewport_width: number | null
        }
        Insert: {
          browser?: string | null
          created_at?: string | null
          id?: string
          screenshot_url: string
          test_case_id?: string | null
          viewport_height?: number | null
          viewport_width?: number | null
        }
        Update: {
          browser?: string | null
          created_at?: string | null
          id?: string
          screenshot_url?: string
          test_case_id?: string | null
          viewport_height?: number | null
          viewport_width?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "visual_baselines_test_case_id_fkey"
            columns: ["test_case_id"]
            isOneToOne: false
            referencedRelation: "test_cases"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      execution_status:
        | "pending"
        | "running"
        | "passed"
        | "failed"
        | "skipped"
        | "cancelled"
      priority_level: "low" | "medium" | "high" | "critical"
      test_status: "draft" | "active" | "inactive" | "archived"
      test_type:
        | "functional"
        | "api"
        | "visual"
        | "performance"
        | "security"
        | "integration"
        | "unit"
      user_role: "admin" | "manager" | "tester" | "developer" | "viewer"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      execution_status: [
        "pending",
        "running",
        "passed",
        "failed",
        "skipped",
        "cancelled",
      ],
      priority_level: ["low", "medium", "high", "critical"],
      test_status: ["draft", "active", "inactive", "archived"],
      test_type: [
        "functional",
        "api",
        "visual",
        "performance",
        "security",
        "integration",
        "unit",
      ],
      user_role: ["admin", "manager", "tester", "developer", "viewer"],
    },
  },
} as const
