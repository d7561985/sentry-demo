<?php

namespace App\Controller;

use App\Service\IntegrationService;
use App\Service\WagerService;
use Psr\Log\LoggerInterface;
use Sentry\SentrySdk;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/api/wager')]
class WagerController extends AbstractController
{
    public function __construct(
        private WagerService $wagerService,
        private LoggerInterface $logger
    ) {}
    
    #[Route('/validate', name: 'wager_validate', methods: ['POST'])]
    public function validate(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);
        
        $userId = $data['user_id'] ?? null;
        $amount = $data['amount'] ?? null;
        $gameId = $data['game_id'] ?? null;
        
        if (!$userId || !$amount || !$gameId) {
            return $this->json([
                'error' => 'user_id, amount, and game_id are required'
            ], 400);
        }
        
        if ($amount <= 0) {
            return $this->json([
                'error' => 'Amount must be positive'
            ], 400);
        }
        
        try {
            \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($userId) {
                $scope->setUser(['id' => $userId]);
            });
            
            $result = $this->wagerService->validateWager($userId, $amount, $gameId);
            
            return $this->json($result);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName()
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/place', name: 'wager_place', methods: ['POST'])]
    public function place(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);
        
        $validationData = $data['validation_data'] ?? null;
        $gameResult = $data['game_result'] ?? null;
        $payout = $data['payout'] ?? 0;
        
        if (!$validationData || !$gameResult) {
            return $this->json([
                'error' => 'validation_data and game_result are required'
            ], 400);
        }
        
        if (!in_array($gameResult, ['win', 'lose'])) {
            return $this->json([
                'error' => 'game_result must be win or lose'
            ], 400);
        }
        
        try {
            $userId = $validationData['user_id'] ?? null;
            if ($userId) {
                \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($userId) {
                    $scope->setUser(['id' => $userId]);
                });
            }
            
            // Ensure validation data has required fields
            if (!isset($validationData['bonus_used'])) {
                $validationData['bonus_used'] = 0.0;
            }
            if (!isset($validationData['real_used'])) {
                $validationData['real_used'] = $validationData['amount'] ?? 0.0;
            }
            
            $result = $this->wagerService->placeWager($validationData, $gameResult, $payout);
            
            return $this->json($result);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName()
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/history/{userId}', name: 'wager_history', methods: ['GET'])]
    public function history(string $userId, Request $request): JsonResponse
    {
        try {
            \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($userId) {
                $scope->setUser(['id' => $userId]);
            });
            
            $limit = $request->query->getInt('limit', 10);
            $limit = min(100, max(1, $limit)); // Clamp between 1 and 100
            
            $result = $this->wagerService->getWagerHistory($userId, $limit);
            
            return $this->json($result);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName()
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/demo/error/{errorType}', name: 'wager_demo_error', methods: ['GET'])]
    public function demoError(string $errorType): JsonResponse
    {
        try {
            $this->wagerService->triggerDemoError($errorType);
            
            return $this->json(['message' => 'Error should have been triggered']);
            
        } catch (\Exception $e) {
            // Explicitly capture exception to Sentry
            \Sentry\captureException($e);
            
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName(),
                'demo' => true
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/test/sentry', name: 'test_sentry', methods: ['GET'])]
    public function testSentry(): JsonResponse
    {
        // Log current Sentry status
        $this->logger->info('Testing Sentry integration', [
            'dsn' => $_ENV['SENTRY_DSN'] ?? 'not set',
            'environment' => $_ENV['APP_ENV'] ?? 'not set',
        ]);
        
        // Create a test exception
        $exception = new \RuntimeException('Test exception for Sentry');
        
        // Capture it
        \Sentry\captureException($exception);
        
        // Also capture a message
        \Sentry\captureMessage('Test message from Wager Service', \Sentry\Severity::info());
        
        return $this->json([
            'message' => 'Test exception and message sent to Sentry',
            'dsn_configured' => !empty($_ENV['SENTRY_DSN']),
            'environment' => $_ENV['APP_ENV'] ?? 'unknown'
        ]);
    }
}