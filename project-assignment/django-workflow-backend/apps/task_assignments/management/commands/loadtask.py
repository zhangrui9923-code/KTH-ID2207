from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.task_assignments.models import TaskAssignment


class Command(BaseCommand):
    help = '创建任务分配的模拟数据'

    def handle(self, *args, **kwargs):
        # 获取现有用户
        try:
            jack = User.objects.get(username='Jack')  # PM (Product Manager)
            antony = User.objects.get(username='Antony')  # Employee in Product department
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('错误: 请先运行 loaduser 命令创建用户')
            )
            return

        now = timezone.now()

        tasks_data = [
            # ========== PENDING 状态 (2条) - Manager 刚创建，还未发送给员工 ==========
            {
                'title': 'Product Feature Analysis - Mobile App',
                'description': 'Analyze user feedback and competitor features for our mobile app. Identify top 5 feature gaps and provide recommendations for Q1 2025 development roadmap.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() + timedelta(days=7),
                'end_date': now.date() + timedelta(days=21),
                'status': 'pending',
                'created_at': now - timedelta(hours=3),
                'updated_at': now - timedelta(hours=3),
            },
            {
                'title': 'Customer Satisfaction Survey Design',
                'description': 'Design a comprehensive customer satisfaction survey for our product line. Include questions about usability, features, pricing, and support. Target: 500+ responses.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() + timedelta(days=5),
                'end_date': now.date() + timedelta(days=19),
                'status': 'pending',
                'created_at': now - timedelta(hours=1),
                'updated_at': now - timedelta(hours=1),
            },
            
            # ========== SENT_TO_EMPLOYEE 状态 (2条) - 已发送给员工，等待员工提交计划 ==========
            {
                'title': 'Q4 Product Performance Report',
                'description': 'Prepare comprehensive Q4 product performance report including sales data, user metrics, customer feedback summary, and competitive analysis. Present findings with visualizations.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() + timedelta(days=2),
                'end_date': now.date() + timedelta(days=14),
                'status': 'sent_to_employee',
                'created_at': now - timedelta(days=2),
                'updated_at': now - timedelta(hours=12),
            },
            {
                'title': 'New Product Line Market Research',
                'description': 'Conduct market research for our proposed eco-friendly product line. Analyze target demographics, market size, pricing strategies, and potential competitors. Provide go/no-go recommendation.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() + timedelta(days=1),
                'end_date': now.date() + timedelta(days=21),
                'status': 'sent_to_employee',
                'created_at': now - timedelta(days=3),
                'updated_at': now - timedelta(days=1),
            },
            
            # ========== PLAN_SUBMITTED 状态 (2条) - 员工已提交计划和预算，等待 Manager 审核 ==========
            {
                'title': 'Product Documentation Update',
                'description': 'Update all product documentation for version 3.0 release. Include user manuals, API documentation, release notes, and training materials. Ensure consistency across all documents.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() - timedelta(days=5),
                'end_date': now.date() + timedelta(days=9),
                'status': 'plan_submitted',
                'employee_plan': '''Work Plan for Product Documentation Update:

Phase 1 (Days 1-3): Content Audit and Planning
- Review all existing documentation for version 2.x
- Identify changes and new features in version 3.0
- Create documentation structure and template
- Assign sections and set internal deadlines

Phase 2 (Days 4-8): Documentation Writing
- User Manual: Update with new UI screenshots and feature descriptions
- API Documentation: Document new endpoints and deprecated features
- Release Notes: Compile all changes, bug fixes, and improvements
- Training Materials: Update slides and video scripts

Phase 3 (Days 9-11): Technical Review
- Internal review by development team
- Accuracy verification of technical details
- Cross-reference checking

Phase 4 (Days 12-14): Final Polish
- Professional editing and proofreading
- Consistency check across all documents
- Format final PDFs and online versions
- Prepare documentation website deployment

Deliverables:
- User Manual (150+ pages)
- API Documentation (complete reference)
- Release Notes (comprehensive changelog)
- Training Materials (slides + 3 tutorial videos)''',
                'estimated_budget': 8500.00,
                'employee_submitted_at': now - timedelta(hours=6),
                'created_at': now - timedelta(days=7),
                'updated_at': now - timedelta(hours=6),
            },
            {
                'title': 'Competitor Product Comparison Matrix',
                'description': 'Create detailed comparison matrix of our products vs. top 5 competitors. Include features, pricing, market position, strengths/weaknesses. Update quarterly.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() - timedelta(days=8),
                'end_date': now.date() + timedelta(days=6),
                'status': 'plan_submitted',
                'employee_plan': '''Work Plan for Competitor Analysis:

Phase 1 (Days 1-3): Data Collection
- Identify top 5 competitors in our market segment
- Sign up for competitor product trials/demos
- Collect pricing information and package details
- Research customer reviews and ratings
- Gather market share and revenue data

Phase 2 (Days 4-7): Feature Analysis
- Create comprehensive feature checklist (100+ features)
- Test and compare each competitor's product
- Document unique selling points
- Identify feature gaps in our product
- Screenshot and document UI/UX differences

Phase 3 (Days 8-11): Strategic Analysis
- SWOT analysis for each competitor
- Pricing strategy comparison
- Market positioning analysis
- Customer satisfaction metrics comparison
- Technology stack evaluation

Phase 4 (Days 12-14): Report Creation
- Build interactive comparison matrix in Excel
- Create executive summary with key findings
- Develop strategic recommendations
- Design presentation slides for stakeholder review

Deliverables:
- Interactive comparison matrix (Excel/Google Sheets)
- Detailed analysis report (40+ pages)
- Executive summary (5 pages)
- Presentation deck (25 slides)
- Quarterly update plan''',
                'estimated_budget': 12000.00,
                'employee_submitted_at': now - timedelta(days=1, hours=3),
                'created_at': now - timedelta(days=10),
                'updated_at': now - timedelta(days=1, hours=3),
            },
            
            # ========== COMPLETED 状态 (2条) - Manager 已批准完成 ==========
            {
                'title': 'Customer Onboarding Process Optimization',
                'description': 'Analyze current customer onboarding process, identify bottlenecks, and propose improvements. Create new onboarding workflow with reduced time-to-value by 30%.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() - timedelta(days=25),
                'end_date': now.date() - timedelta(days=5),
                'status': 'completed',
                'employee_plan': '''Work Plan for Onboarding Optimization:

Phase 1 (Days 1-5): Current State Analysis
- Map existing onboarding process (20+ steps)
- Interview 15 recent customers about their experience
- Analyze support tickets related to onboarding
- Measure current time-to-value metrics
- Identify pain points and drop-off stages

Phase 2 (Days 6-10): Best Practices Research
- Research industry best practices
- Analyze competitor onboarding processes
- Study successful SaaS onboarding examples
- Benchmark against industry standards

Phase 3 (Days 11-15): New Process Design
- Redesign onboarding workflow
- Create step-by-step process documentation
- Design welcome email sequence
- Develop in-app tutorial flow
- Plan automated touchpoints

Phase 4 (Days 16-20): Implementation Planning
- Create implementation roadmap
- Develop training materials for support team
- Design metrics dashboard
- Plan A/B testing strategy
- Document success criteria

Deliverables:
- Current state analysis report
- New onboarding process documentation
- Welcome email templates (5 emails)
- In-app tutorial scripts
- Implementation guide
- Success metrics framework''',
                'estimated_budget': 15000.00,
                'employee_submitted_at': now - timedelta(days=18),
                'created_at': now - timedelta(days=30),
                'updated_at': now - timedelta(days=3),
            },
            {
                'title': 'Product Pricing Strategy Analysis',
                'description': 'Conduct comprehensive pricing analysis for our product tiers. Analyze customer willingness to pay, competitive pricing, and propose optimized pricing structure to increase revenue by 15%.',
                'manager': jack,
                'employee': antony,
                'start_date': now.date() - timedelta(days=40),
                'end_date': now.date() - timedelta(days=12),
                'status': 'completed',
                'employee_plan': '''Work Plan for Pricing Strategy Analysis:

Phase 1 (Days 1-7): Data Collection & Analysis
- Analyze historical sales data across all tiers
- Survey 200+ customers on pricing perception
- Study customer upgrade/downgrade patterns
- Calculate customer lifetime value by tier
- Analyze price elasticity

Phase 2 (Days 8-14): Competitive Benchmarking
- Deep-dive into competitor pricing models
- Compare feature-to-price ratios
- Analyze market positioning
- Study psychological pricing tactics
- Research industry pricing trends

Phase 3 (Days 15-21): Financial Modeling
- Build revenue projection models
- Analyze impact of different pricing scenarios
- Calculate optimal price points per tier
- Model customer migration between tiers
- Project ROI of pricing changes

Phase 4 (Days 22-28): Strategy Development
- Design new pricing structure (3-4 tiers)
- Create pricing page wireframes
- Develop positioning strategy
- Plan pricing communication strategy
- Design grandfathering policy for existing customers

Deliverables:
- Comprehensive pricing analysis report (60+ pages)
- Financial models and projections
- Recommended pricing structure
- Implementation roadmap
- Customer communication plan
- Risk analysis and mitigation strategies
- A/B testing plan for pricing page''',
                'estimated_budget': 18500.00,
                'employee_submitted_at': now - timedelta(days=35),
                'created_at': now - timedelta(days=45),
                'updated_at': now - timedelta(days=10),
            },
        ]

        created_count = 0
        for task_data in tasks_data:
            title = task_data['title']
            
            # 检查是否已存在同名任务
            if TaskAssignment.objects.filter(
                title=title,
                manager=jack,
                employee=antony
            ).exists():
                self.stdout.write(
                    self.style.WARNING(f'任务 "{title}" 已存在，跳过')
                )
                continue
            
            # 创建任务
            TaskAssignment.objects.create(**task_data)
            
            created_count += 1
            status_display = dict(TaskAssignment.STATUS_CHOICES)[task_data['status']]
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ 成功创建任务: {title[:50]}... ({status_display})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n总计创建 {created_count} 条任务分配记录')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Manager: Jack (PM) → Employee: Antony (Product Department)')
        )
