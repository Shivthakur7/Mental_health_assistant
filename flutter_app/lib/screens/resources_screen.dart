import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import '../config/app_theme.dart';

class ResourcesScreen extends StatefulWidget {
  const ResourcesScreen({super.key});

  @override
  State<ResourcesScreen> createState() => _ResourcesScreenState();
}

class _ResourcesScreenState extends State<ResourcesScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;

  final List<HelplineResource> _helplines = [
    HelplineResource(
      name: 'National Suicide Prevention Lifeline',
      number: '988',
      description: '24/7 crisis support for suicidal thoughts',
      icon: Icons.phone_in_talk,
      color: Colors.red,
    ),
    HelplineResource(
      name: 'Crisis Text Line',
      number: '741741',
      description: 'Text HOME for crisis support',
      icon: Icons.message,
      color: Colors.blue,
    ),
    HelplineResource(
      name: 'SAMHSA National Helpline',
      number: '1-800-662-4357',
      description: 'Treatment referral and information service',
      icon: Icons.support_agent,
      color: Colors.green,
    ),
    HelplineResource(
      name: 'NAMI Helpline',
      number: '1-800-950-6264',
      description: 'Mental health support and information',
      icon: Icons.psychology,
      color: Colors.purple,
    ),
  ];

  final List<ArticleResource> _articles = [
    ArticleResource(
      title: 'Understanding Anxiety',
      description: 'Learn about anxiety symptoms and coping strategies',
      url: 'https://www.nimh.nih.gov/health/topics/anxiety-disorders',
      category: 'Anxiety',
      readTime: '5 min read',
      icon: Icons.article,
    ),
    ArticleResource(
      title: 'Depression: What You Need to Know',
      description: 'Comprehensive guide to understanding depression',
      url: 'https://www.nimh.nih.gov/health/topics/depression',
      category: 'Depression',
      readTime: '8 min read',
      icon: Icons.book,
    ),
    ArticleResource(
      title: 'Mindfulness and Mental Health',
      description: 'How mindfulness can improve your mental wellbeing',
      url: 'https://www.mindful.org/mindfulness-mental-health/',
      category: 'Mindfulness',
      readTime: '6 min read',
      icon: Icons.self_improvement,
    ),
    ArticleResource(
      title: 'Building Resilience',
      description: 'Strategies to build mental resilience and cope with stress',
      url: 'https://www.apa.org/topics/resilience',
      category: 'Resilience',
      readTime: '7 min read',
      icon: Icons.fitness_center,
    ),
  ];

  final List<TechniqueResource> _techniques = [
    TechniqueResource(
      title: '4-7-8 Breathing',
      description: 'A simple breathing technique to reduce anxiety',
      steps: [
        'Inhale through your nose for 4 counts',
        'Hold your breath for 7 counts',
        'Exhale through your mouth for 8 counts',
        'Repeat 3-4 times',
      ],
      icon: Icons.air,
      color: Colors.blue,
    ),
    TechniqueResource(
      title: '5-4-3-2-1 Grounding',
      description: 'Use your senses to ground yourself in the present',
      steps: [
        'Name 5 things you can see',
        'Name 4 things you can touch',
        'Name 3 things you can hear',
        'Name 2 things you can smell',
        'Name 1 thing you can taste',
      ],
      icon: Icons.visibility,
      color: Colors.green,
    ),
    TechniqueResource(
      title: 'Progressive Muscle Relaxation',
      description: 'Systematically tense and relax muscle groups',
      steps: [
        'Start with your toes, tense for 5 seconds',
        'Release and notice the relaxation',
        'Move up to your calves, thighs, etc.',
        'Work your way up to your head',
        'End with deep breathing',
      ],
      icon: Icons.accessibility_new,
      color: Colors.orange,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _launchPhone(String phoneNumber) async {
    final Uri phoneUri = Uri(scheme: 'tel', path: phoneNumber);
    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not launch phone dialer'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _launchUrl(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not launch URL'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // App Bar
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: Icon(
                        Icons.arrow_back,
                        color: AppTheme.primaryBlue,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        'Mental Health Resources',
                        style: GoogleFonts.poppins(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.primaryBlue,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(width: 48),
                  ],
                ),
              ),

              // Tab Bar
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: TabBar(
                  controller: _tabController,
                  labelColor: Colors.white,
                  unselectedLabelColor: AppTheme.primaryBlue,
                  indicator: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  labelStyle: GoogleFonts.poppins(
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                  tabs: const [
                    Tab(text: 'Helplines'),
                    Tab(text: 'Articles'),
                    Tab(text: 'Techniques'),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Tab Bar View
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildHelplinesTab(),
                    _buildArticlesTab(),
                    _buildTechniquesTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHelplinesTab() {
    return AnimationLimiter(
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _helplines.length,
        itemBuilder: (context, index) {
          final helpline = _helplines[index];
          return AnimationConfiguration.staggeredList(
            position: index,
            duration: const Duration(milliseconds: 375),
            child: SlideAnimation(
              verticalOffset: 50.0,
              child: FadeInAnimation(
                child: Container(
                  margin: const EdgeInsets.only(bottom: 16),
                  padding: const EdgeInsets.all(16),
                  decoration: AppDecorations.softCard,
                  child: Row(
                    children: [
                      Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          color: helpline.color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Icon(
                          helpline.icon,
                          color: helpline.color,
                          size: 30,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              helpline.name,
                              style: GoogleFonts.poppins(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.grey.shade800,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              helpline.description,
                              style: GoogleFonts.poppins(
                                fontSize: 14,
                                color: Colors.grey.shade600,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              helpline.number,
                              style: GoogleFonts.poppins(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: helpline.color,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () => _launchPhone(helpline.number),
                        icon: Icon(
                          Icons.phone,
                          color: helpline.color,
                        ),
                        style: IconButton.styleFrom(
                          backgroundColor: helpline.color.withOpacity(0.1),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildArticlesTab() {
    return AnimationLimiter(
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _articles.length,
        itemBuilder: (context, index) {
          final article = _articles[index];
          return AnimationConfiguration.staggeredList(
            position: index,
            duration: const Duration(milliseconds: 375),
            child: SlideAnimation(
              verticalOffset: 50.0,
              child: FadeInAnimation(
                child: GestureDetector(
                  onTap: () => _launchUrl(article.url),
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: AppDecorations.softCard,
                    child: Row(
                      children: [
                        Container(
                          width: 60,
                          height: 60,
                          decoration: BoxDecoration(
                            gradient: AppTheme.primaryGradient,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Icon(
                            article.icon,
                            color: Colors.white,
                            size: 30,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: AppTheme.primaryBlue.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      article.category,
                                      style: GoogleFonts.poppins(
                                        fontSize: 10,
                                        fontWeight: FontWeight.w600,
                                        color: AppTheme.primaryBlue,
                                      ),
                                    ),
                                  ),
                                  const Spacer(),
                                  Text(
                                    article.readTime,
                                    style: GoogleFonts.poppins(
                                      fontSize: 12,
                                      color: Colors.grey.shade500,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                article.title,
                                style: GoogleFonts.poppins(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.grey.shade800,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                article.description,
                                style: GoogleFonts.poppins(
                                  fontSize: 14,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.arrow_forward_ios,
                          color: Colors.grey.shade400,
                          size: 16,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTechniquesTab() {
    return AnimationLimiter(
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _techniques.length,
        itemBuilder: (context, index) {
          final technique = _techniques[index];
          return AnimationConfiguration.staggeredList(
            position: index,
            duration: const Duration(milliseconds: 375),
            child: SlideAnimation(
              verticalOffset: 50.0,
              child: FadeInAnimation(
                child: Container(
                  margin: const EdgeInsets.only(bottom: 16),
                  padding: const EdgeInsets.all(16),
                  decoration: AppDecorations.softCard,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: technique.color.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              technique.icon,
                              color: technique.color,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  technique.title,
                                  style: GoogleFonts.poppins(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.grey.shade800,
                                  ),
                                ),
                                Text(
                                  technique.description,
                                  style: GoogleFonts.poppins(
                                    fontSize: 14,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      ...technique.steps.asMap().entries.map((entry) {
                        int stepIndex = entry.key;
                        String step = entry.value;
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: 24,
                                height: 24,
                                decoration: BoxDecoration(
                                  color: technique.color,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Center(
                                  child: Text(
                                    '${stepIndex + 1}',
                                    style: GoogleFonts.poppins(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  step,
                                  style: GoogleFonts.poppins(
                                    fontSize: 14,
                                    color: Colors.grey.shade700,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class HelplineResource {
  final String name;
  final String number;
  final String description;
  final IconData icon;
  final Color color;

  HelplineResource({
    required this.name,
    required this.number,
    required this.description,
    required this.icon,
    required this.color,
  });
}

class ArticleResource {
  final String title;
  final String description;
  final String url;
  final String category;
  final String readTime;
  final IconData icon;

  ArticleResource({
    required this.title,
    required this.description,
    required this.url,
    required this.category,
    required this.readTime,
    required this.icon,
  });
}

class TechniqueResource {
  final String title;
  final String description;
  final List<String> steps;
  final IconData icon;
  final Color color;

  TechniqueResource({
    required this.title,
    required this.description,
    required this.steps,
    required this.icon,
    required this.color,
  });
}
