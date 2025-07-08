<?php

namespace App\Controller;

use App\Service\BonusService;
use App\Service\IntegrationService;
use Sentry\SentrySdk;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/api/bonus')]
class BonusController extends AbstractController
{
    public function __construct(
        private BonusService $bonusService
    ) {}
    
    #[Route('/claim', name: 'bonus_claim', methods: ['POST'])]
    public function claim(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);
        $userId = $data['user_id'] ?? null;
        
        if (!$userId) {
            return $this->json(['error' => 'user_id is required'], 400);
        }
        
        try {
            \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($userId) {
                $scope->setUser(['id' => $userId]);
            });
            
            $result = $this->bonusService->claimWelcomeBonus($userId, $request);
            
            return $this->json($result);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName()
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/progress/{userId}', name: 'bonus_progress', methods: ['GET'])]
    public function progress(string $userId, Request $request): JsonResponse
    {
        try {
            \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($userId) {
                $scope->setUser(['id' => $userId]);
            });
            
            $result = $this->bonusService->getProgress($userId);
            
            return $this->json($result);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName()
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/convert/{userId}', name: 'bonus_convert', methods: ['POST'])]
    public function convert(string $userId, Request $request): JsonResponse
    {
        try {
            \Sentry\configureScope(function (\Sentry\State\Scope $scope) use ($userId) {
                $scope->setUser(['id' => $userId]);
            });
            
            $result = $this->bonusService->convertBonusToReal($userId);
            
            return $this->json($result);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName()
            ], $e->getCode() ?: 500);
        }
    }
    
    #[Route('/demo/error/{errorType}', name: 'bonus_demo_error', methods: ['GET'])]
    public function demoError(string $errorType): JsonResponse
    {
        try {
            $this->bonusService->triggerDemoError($errorType);
            
            return $this->json(['message' => 'Error should have been triggered']);
            
        } catch (\Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'type' => (new \ReflectionClass($e))->getShortName(),
                'demo' => true
            ], $e->getCode() ?: 500);
        }
    }
}