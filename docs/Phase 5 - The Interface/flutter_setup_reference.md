# Flutter Setup Commands
To initialize the frontend application, run the following commands in the `query_voice_root` directory:

```bash
# Create the flutter project
flutter create frontend_app

# Navigate to the project directory
cd frontend_app

# Add required dependencies
flutter pub add http google_fonts
```

# frontend_app/lib/main.dart
Replace the default `lib/main.dart` with the following skeleton code which implements the "Enterprise AI" theme and the Bottom Navigation Bar architecture.

```dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

void main() {
  runApp(const QueryVoiceApp());
}

class QueryVoiceApp extends StatelessWidget {
  const QueryVoiceApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QueryVoice',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF121212), // Matte Black
        primaryColor: Colors.deepPurpleAccent,
        colorScheme: const ColorScheme.dark(
          primary: Colors.deepPurpleAccent,
          secondary: Colors.deepPurple,
          surface: Color(0xFF1E1E1E), // Dark Grey/Matte for cards
          error: Colors.redAccent,
        ),
        textTheme: TextTheme(
          bodyLarge: GoogleFonts.inter(color: const Color(0xFFF5F5DC)), // Cream White
          bodyMedium: GoogleFonts.inter(color: const Color(0xFFF5F5DC)),
          titleLarge: GoogleFonts.inter(color: const Color(0xFFF5F5DC), fontWeight: FontWeight.bold),
          labelSmall: GoogleFonts.robotoMono(color: const Color(0xFFF5F5DC)), // For SQL blocks
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF121212),
          elevation: 0,
          centerTitle: true,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Color(0xFF1E1E1E),
          selectedItemColor: Colors.deepPurpleAccent,
          unselectedItemColor: Colors.grey,
        ),
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({Key? key}) : super(key: key);

  @override
  _MainNavigationScreenState createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const VoiceChatScreen(),
    const DatabaseDashboardScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.mic),
            label: 'Query',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.storage),
            label: 'Database',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

// ==========================================
// Placeholder Screens
// ==========================================

class VoiceChatScreen extends StatelessWidget {
  const VoiceChatScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('QueryVoice Agent'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Voice/Chat Screen (Core)'),
            const SizedBox(height: 20),
            // Placeholder for the "Brain" Animation
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'Brain Animation Placeholder\n[User -> Router -> RAG -> Generator -> Evaluator -> Output]',
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: Theme.of(context).colorScheme.primary,
        child: const Icon(Icons.mic, color: Colors.white),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }
}

class DatabaseDashboardScreen extends StatelessWidget {
  const DatabaseDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Database Dashboard'),
      ),
      body: const Center(
        child: Text('Local queryvoice_local.db Status'),
      ),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile & Settings'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('QueryVoice Mission Statement'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Connect New Database (Coming Soon)'),
            ),
          ],
        ),
      ),
    );
  }
}
```
